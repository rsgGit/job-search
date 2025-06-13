import logging
import asyncio
from job_scraper_scheduler import scrape_jobs_from_each_country
from db_utils import remove_jobs_that_are_older_than_three_months


def log(msg):
    logging.info(msg)

def scrape_jobs():
    log("Started scheduler for scraping jobs")
    log("Started to scrape for jobs")
    asyncio.run(scrape_jobs_from_each_country())
    log("Scraping completed")
    log("Started to remove jobs older than 3 months")
    remove_jobs_that_are_older_than_three_months()
    log("Removed jobs older than 3 months")
    log("Scheduler ended")

log("Schedule Test working")