from flask import Flask
from flask_cors import CORS
from jobspy import scrape_jobs

import pandas as pd
import asyncio
import aiohttp
from .db_utils import get_all_countries, get_jobs_with_sponsorship
import os
app = Flask(__name__)

@app.route("/")
def home():
    return "Hellooo fromm Railway!"

@app.route("/hello")
def home():
    return "Hellooo!"


@app.route('/get-countries', methods=['GET'])
def get_countries():
    return jsonify(get_all_countries())

# @app.route('/load-jobs', methods=['GET'])
# def load_jobs():
#     # timeout = aiohttp.ClientTimeout(total=60)
#     keyword = request.args.get('keyword', default=None, type=str)
#     location = request.args.get('location', default=None, type=str)
#     date_posted = request.args.get('date_posted', default=None, type=str)
#     page = int(request.args.get('page', 1))
#     if keyword=="": keyword = None
#     if location=="": location = None
#     if date_posted=="": date_posted = None
#     page_data = get_jobs_with_sponsorship(keyword, location, date_posted, page, 50)
#     jobs = page_data['data']
#     if isinstance(page_data.get('data'), pd.DataFrame):
#         page_data['data'] = page_data['data'].to_dict(orient='records')
#     return jsonify(page_data)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)