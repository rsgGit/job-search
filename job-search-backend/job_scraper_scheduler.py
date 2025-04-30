import asyncio
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from timeit import default_timer
import multiprocessing
from datetime import datetime
from db_utils import create_database_if_not_exists, create_jobs_table, add_jobs_to_table, create_countries_table, add_countries, get_countries_that_are_not_updated
from config import Config
from flask_mysqldb import MySQL
from jobspy import scrape_jobs
import time
import logging
from prediction import get_predictions

logging.basicConfig(
    filename='logs/app.log',
    level = logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(message)s'
)

START_TIME = default_timer()
executor = ThreadPoolExecutor()

def log(msg):
    logging.info(msg)
    # now = datetime.now().strftime('%H:%M:%S.%f'[:-3])
    # print(f"[{now}] {msg}")

def prepare_db():
    create_database_if_not_exists()
    create_jobs_table()
    create_countries_table()
    add_countries()

async def scrape(platform, start_index, results_per_batch, keyword, location, date_posted):
    """Scrapes job listings from a platform."""
    try:
        
        loop = asyncio.get_event_loop()
        search_term = "'sponsorship' OR 'visa' OR 'relocation' OR 'h1b' OR 'h1-b' OR 'h-1b'"
        
        def blocking_scrape():
            return scrape_jobs(
                site_name= platform,
                search_term=search_term,
                google_search_term=search_term,
                results_wanted=results_per_batch,
                offset=start_index,
                location = location,
                country_indeed = location,
                hours_old=168,
                linkedin_fetch_description=True,
            )
        jobs = await loop.run_in_executor(executor, blocking_scrape)
        elapsed_time = default_timer() - START_TIME
        log(f"✅ {platform} | Offset {start_index}: {len(jobs)} results for country {location}. Completed in {elapsed_time:.2f}s")
        return jobs
    except Exception as e:
        log(f"❌ Error scraping {platform} at offset {start_index} for country {location}: {e}")
        return pd.DataFrame()


async def scrape_until_done(platform, location):
    log(f"Scraping started in {platform} in location {location}")
    job_results = []
    offset = 0
    number_of_results = 1000

    while True:
        df = await scrape(platform, offset, number_of_results, keyword=None, location=location, date_posted=None)
        if df.empty:
            log(f"🛑 No more results from {platform} | Location: {location}")
            break
        job_results.append(df)
        offset += number_of_results

    if job_results:
        combined = pd.concat(job_results, ignore_index=True)
        log(f"✅ Returned {len(combined)} results from {platform}, {location}")
        return combined
    else:
        return pd.DataFrame()

async def scrape_all_platforms_for_location(location):
    tasks = [scrape_until_done(platform, location) for platform in ['indeed', 'glassdoor', 'linkedin']]
    results = await asyncio.gather(*tasks)
    combined = pd.concat([df for df in results if not df.empty], ignore_index=True)
    combined = await get_predictions(location, combined)
    add_jobs_to_table(combined, location)
    log(f"🌍 Done with location: {location} | Total Jobs: {len(combined)}")
    return combined  # ✅ Don't forget this

async def scrape_jobs_from_each_country():
    prepare_db()
    batch_size = 5
    countries = get_countries_that_are_not_updated()
    batched_countries = [countries[i:i+batch_size] for i in range(0, len(countries), batch_size)]
    for i, batch in enumerate(batched_countries):
        log(f"----------Started scraping for batch {i+1}----------")
        start = default_timer()
        tasks = [scrape_all_platforms_for_location(location) for location in batch]
        results = await asyncio.gather(*tasks)
        elapsed_time = default_timer() - start
        log(f"Completed all scraping for batch {i+1} in {elapsed_time:.2f}s")
        if(i<len(batched_countries)-1): time.sleep(120)
    elapsed_time = default_timer() - START_TIME
    log(f"🎉 Completed all scraping in {elapsed_time:.2f}s")

# Run the full async process
asyncio.run(scrape_jobs_from_each_country())
