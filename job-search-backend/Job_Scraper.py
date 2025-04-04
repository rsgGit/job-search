from jobspy import scrape_jobs
import asyncio
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from timeit import default_timer
import multiprocessing

START_TIME = default_timer()

# Dynamically set workers based on CPU cores
MAX_WORKERS = min(20, multiprocessing.cpu_count() * 2)  

def scrape(platform, start_index, results_per_batch, keyword, location, date_posted):
    """Scrapes job listings from a platform."""
    try:
        search_term = "'sponsorship' OR 'visa' OR 'relocation' OR 'h1b' OR 'h1-b' OR 'h-1b'"
        jobs = scrape_jobs(
            site_name=[platform],
            search_term=keyword,
            google_search_term=keyword,
            results_wanted=results_per_batch,
            offset=start_index,
            location = location,
            date_posted = date_posted,
            linkedin_fetch_description=False,
        )
        print(f"✅ {platform} | Offset {start_index}: {len(jobs)} results")
        return jobs
    except Exception as e:
        print(f"❌ Error scraping {platform} at offset {start_index}: {e}")
        return pd.DataFrame()

async def scrape_jobs_from_platform(platform, num_results, keyword, location, date_posted):
    """Asynchronously scrape jobs from a platform in parallel batches."""
    batch_size = 10  # Larger batch size reduces API calls
    offsets = list(range(0, num_results, batch_size))

    loop = asyncio.get_running_loop()
    semaphore = asyncio.Semaphore(MAX_WORKERS)  # Limit concurrent tasks

    async def bounded_scrape(offset):
        async with semaphore:
            return await loop.run_in_executor(None, scrape, platform, offset, batch_size, keyword, location, date_posted)

    tasks = [bounded_scrape(offset) for offset in offsets]
    results = await asyncio.gather(*tasks)

    return pd.concat(results, ignore_index=True) if results else pd.DataFrame()

async def get_jobs(keyword=None, location = None, date_posted = None):
    """Runs all job scraping tasks in parallel for maximum speed."""
    platforms = ['indeed']
    num_results = 100  # Fetch more results per platform

    tasks = [scrape_jobs_from_platform(platform, num_results, keyword, location, date_posted) for platform in platforms]
    
    results = await asyncio.gather(*tasks)
    final_df = pd.concat(results, ignore_index=True)

    elapsed_time = default_timer() - START_TIME
    print(f"✅ Completed in {elapsed_time:.2f}s | Total Jobs Scraped: {len(final_df)}")
    return final_df

if __name__ == "__main__":
    asyncio.run(get_jobs())
