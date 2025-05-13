from flask import Flask, jsonify, request
from flask_cors import CORS
from jobspy import scrape_jobs
import pandas as pd
import asyncio
import aiohttp
from .db_utils import get_all_countries, get_jobs_with_sponsorship, create_database_if_not_exists, create_jobs_table, add_jobs_to_table, create_countries_table, add_countries, get_countries_that_are_not_updated, remove_jobs_that_are_older_than_three_months
import os
from .job_scraper_scheduler import scrape_jobs_from_each_country
from flask_apscheduler import APScheduler
import logging
from timeit import default_timer

class Config:
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = 'Asia/Qatar'  # your desired timezone

app = Flask(__name__)
CORS(app, origins=["https://rsggit.github.io"])

app.config.from_object(Config())
logging.basicConfig(
    # filename= os.path.join(base_path, "logs/app.log"),
    level = logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(message)s'
)

START_TIME = default_timer()

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

def log(msg):
    logging.info(msg)

def prepare_db():
    log("Preparing the database...")
    create_database_if_not_exists()
    create_jobs_table()
    create_countries_table()
    add_countries()

prepare_db()

@app.route("/")
def home():
    return "Hellooo fromm Railway!"

@app.route("/hello")
def hello():
    return "Hellooo!"


@app.route('/get-countries', methods=['GET'])
def get_countries():
    return jsonify(get_all_countries())

@app.route('/load-jobs', methods=['GET'])
def load_jobs():
    # timeout = aiohttp.ClientTimeout(total=60)
    keyword = request.args.get('keyword', default=None, type=str)
    location = request.args.get('location', default=None, type=str)
    date_posted = request.args.get('date_posted', default=None, type=str)
    page = int(request.args.get('page', 1))
    if keyword=="": keyword = None
    if location=="": location = None
    if date_posted=="": date_posted = None
    page_data = get_jobs_with_sponsorship(keyword, location, date_posted, page, 50)
    jobs = page_data['data']
    if isinstance(page_data.get('data'), pd.DataFrame):
        page_data['data'] = page_data['data'].to_dict(orient='records')
    return jsonify(page_data)

@scheduler.task('cron', id='daily_scrape', hour = 16, minute = 12)
def scrape_jobs():
    log("Started scheduler for scraping jobs")
    log("Started to scrape for jobs")
    asyncio.run(scrape_jobs_from_each_country())
    log("Scraping completed")
    log("Started to remove jobs older than 3 months")
    remove_jobs_that_are_older_than_three_months()
    log("Removed jobs older than 3 months")
    log("Scheduler ended")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
