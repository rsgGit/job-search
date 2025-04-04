from jobspy import scrape_jobs
import concurrent.futures
import pandas as pd
import asyncio
from concurrent.futures import ThreadPoolExecutor
from timeit import default_timer
import aiohttp
import requests
import time
from bs4 import BeautifulSoup;
import requests;
from fake_useragent import UserAgent;

START_TIME = default_timer()

def scrape_jobs_from_platform(platform, start_indices, number_of_results):
    elapsed_time = default_timer() - START_TIME
    completed_at = "{:5.2f}s".format(elapsed_time)
    search_term = "'sponsorship provided' OR 'sponsorship is provided' OR 'require visa' OR 'relocation provided' OR 'h1b' OR 'h1-b' OR 'h-1b'"
    jobs = scrape_jobs(
            site_name=[platform],
            search_term = search_term,
            google_search_term = "sponsorship is provided",
            # location = "United Kingdom",
            results_wanted = number_of_results,
            offset = start_indices,
            linkedin_fetch_description=False,
            # hours_old = 24,
            # country_indeed = "United Kingdom",
    )
    elapsed_time = default_timer() - START_TIME
    completed_at = "{:5.2f}s".format(elapsed_time)
    return jobs

async def scrape_all_linkedin_jobs():
    offsets = [i * 5 for i in range(5)]
    with ThreadPoolExecutor(max_workers=5) as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(executor, scrape_jobs_from_platform, 'linkedin', offset, 5)
            for offset in offsets
        ]
        results = await asyncio.gather(*tasks)  
    return results

async def get_linkedin_job_description(session, job, delay=0.5):
    """Fetch LinkedIn job description with infinite retry for status 429 and connection errors."""
    response = None
    ua = UserAgent()
    headers = {"User-Agent":ua.random}
    while response is None or response.status == 429:
        async with session.get(job.iloc[0]['job_url'], headers=headers) as r:
                response = r
                if response.status == 429 and delay<4:  
                    # print(f"Rate limited. Retrying in {delay} seconds...")
                    headers["User-Agent"] = ua.random
                    await asyncio.sleep(delay)
                    delay *= 2 
                    continue
                elif response.status == 429: 
                    job.at[job.index[0], 'description'] = ''
                    return job
                
                text = await r.text()
                soup = BeautifulSoup(text, 'html.parser')
                description = ""
                divs = soup.find_all("div", {"class": "description__text description__text--rich"})
                if (len(divs)>0):
                    inside_divs = divs[0].find_all("div")
                    if(len(inside_divs)>0): description = inside_divs[0].decode_contents()
                # print(f"✅ Success: {job.iloc[0]['job_url']} | Status: {response.status}")
                job.at[job.index[0], 'description'] = description
                return job


async def get_all_job_descriptions(results):
    offsets = [i * 1 for i in range(25)]
    async with aiohttp.ClientSession() as session:
        tasks = [
            get_linkedin_job_description(session, results.iloc[offset:offset+1])
            for offset in offsets
        ]
        r = await asyncio.gather(*tasks) 
        return pd.concat(r, ignore_index=True)

async def get_linkedin_jobs():
    l_results = await scrape_all_linkedin_jobs()
    l_results = pd.concat(l_results, ignore_index=True)
    l_jobs = await get_all_job_descriptions(l_results)
    return l_jobs

async def get_jobs():
    timeout = aiohttp.ClientTimeout(total=60)  # Set timeout here
    loop = asyncio.get_running_loop()
    i_results_future = loop.run_in_executor(None, scrape_jobs_from_platform, 'indeed', 0, 100)
    g_results_future = loop.run_in_executor(None, scrape_jobs_from_platform, 'glassdoor', 0, 100)
    # l_results_future = get_linkedin_jobs()
    # i_results, g_results, l_results = await asyncio.gather(i_results_future, g_results_future, l_results_future)
    i_results, g_results = await asyncio.gather(i_results_future, g_results_future)
    # print("scraped")
    # final_df = pd.concat([i_results, g_results, l_results], ignore_index=True)
    final_df = pd.concat([i_results, g_results], ignore_index=True)

    elapsed_time = default_timer() - START_TIME
    completed_at = "{:5.2f}s".format(elapsed_time)
    print(f"Completed at: {completed_at}")
    return final_df
asyncio.run(get_jobs()) 