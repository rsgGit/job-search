import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb
from .config import Config
import pandas as pd
from .countries import COUNTRIES
from datetime import date
import math
import datetime
from dateutil.relativedelta import relativedelta

def get_raw_connection():
    return MySQLdb.connect(
        host = Config.MYSQL_HOST,
        user = Config.MYSQL_USER,
        passwd = Config.MYSQL_PASSWORD,
        port = Config.MYSQL_PORT
    )

def get_db_connection():
    return MySQLdb.connect(
        host = Config.MYSQL_HOST,
        user = Config.MYSQL_USER,
        passwd = Config.MYSQL_PASSWORD,
        db = Config.MYSQL_DB,
        port = Config.MYSQL_PORT
    )

def create_database_if_not_exists():
    conn = get_raw_connection()
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB}")
    print(f"Database {Config.MYSQL_DB} ensured.")
    cursor.close()
    conn.close()

def create_jobs_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            job_id VARCHAR(255) UNIQUE,
            title VARCHAR(255),
            company VARCHAR(255),
            description TEXT,
            location VARCHAR(255),
            country VARCHAR(255),
            url TEXT,
            platform VARCHAR(100),
            date_posted DATE,
            company_logo TEXT,
            sponsorship_provided_probability DOUBLE,
            sponsorship_not_provided_probability DOUBLE,
            sponsorship_uncertain_probability DOUBLE,
            sponsorship_provided VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.close()
    conn.close()

def create_countries_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS countries (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

def add_jobs_to_table(jobs, country):
    if not jobs.empty:
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            jobs = jobs.where(pd.notnull(jobs), None)

            data_to_insert = [
                (row['id'], row['title'], row['company'], row['description'], row['location'], country, row['job_url'], row['site'], row['date_posted'], row['company_logo'], row['sponsorship_provided_probability'], row['sponsorship_not_provided_probability'], row['sponsorship_uncertain_probability'], row['sponsorship_provided']) 
                for _, row in jobs.iterrows()
            ]            
            insert_stmt = """
                INSERT INTO jobs (job_id, title, company, description, location, country, url, platform, date_posted, company_logo, sponsorship_provided_probability, sponsorship_not_provided_probability, sponsorship_uncertain_probability, sponsorship_provided) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,  %s, %s, %s, %s,  %s)
                ON DUPLICATE KEY UPDATE
                    title = VALUES(title),
                    company = VALUES(company),
                    description = VALUES(description),
                    location = VALUES(location),
                    country = VALUES(country),
                    url = VALUES(url),
                    platform = VALUES(platform),
                    date_posted = VALUES(date_posted),
                    company_logo = VALUES(company_logo),
                    sponsorship_provided_probability = VALUES(sponsorship_provided_probability),
                    sponsorship_not_provided_probability = VALUES(sponsorship_not_provided_probability),
                    sponsorship_uncertain_probability = VALUES(sponsorship_uncertain_probability),
                    sponsorship_provided = VALUES(sponsorship_provided)

            """
            cursor.executemany(insert_stmt, data_to_insert)      

            query ="""
                UPDATE countries SET updated_at = CURRENT_TIMESTAMP WHERE name = %s
            """
            cursor.execute(query, (country,))
            connection.commit()
        finally:
            connection.close()

def add_countries():
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        data_to_insert = [(country,) for country in COUNTRIES]
        insert_stmt = """
            INSERT IGNORE INTO countries (name)
            VALUES (%s)        
        """
        cursor.executemany(insert_stmt, data_to_insert)
        connection.commit()
    finally:
        connection.close()

def apply_predictions(jobs):
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        data_to_update = [(job['sponsorship_provided_probability'], job['sponsorship_not_provided_probability'], job['sponsorship_uncertain_probability'], job['sponsorship_provided'], job['id']) for index, job in jobs.iterrows()]
        stmt = """
            UPDATE jobs SET sponsorship_provided_probability = %s, sponsorship_not_provided_probability = %s, sponsorship_uncertain_probability = %s, sponsorship_provided = %s WHERE id = %s;
        """
        cursor.executemany(stmt, data_to_update)
        connection.commit()
    finally:
        connection.close()

def get_countries_that_are_not_updated():
    connection = get_db_connection()
    today = date.today()

    query="""
        SELECT name FROM countries WHERE updated_at is null or DATE(updated_at) != %s
    """
    try:
        cursor = connection.cursor()
        cursor.execute(query, (today,))
        results = cursor.fetchall()
        return [res[0] for res in results]
    finally:
        connection.close()


def get_all_countries():
    return ["A", "B", "C"]
    # connection = get_db_connection()

    # query="""
    #     SELECT name FROM countries
    # """
    # try:
    #     cursor = connection.cursor()
    #     cursor.execute(query)
    #     results = cursor.fetchall()
    #     return [res[0] for res in results]
    # finally:
    #     connection.close()

def get_start_date(date_posted):
    today = date.today()
    start_date = None
    if date_posted == '24 hours ago':
        start_date = today - datetime.timedelta(days=1)
    elif date_posted == '3 days ago':
        start_date = today - datetime.timedelta(days=3)
    elif date_posted == '1 week ago':
        start_date = today - datetime.timedelta(weeks=1)
    elif date_posted == '1 month ago':
        start_date = today - relativedelta(months=1)

def get_all_jobs(keyword, location, date_posted, page, elements_to_display=50):
    connection = get_db_connection()
    if(elements_to_display!= None and page!=None):
        offset = (page - 1) * elements_to_display
    # Default to wildcard if empty
    keyword = keyword if keyword else ''
    location = location if location else ''
    start_date = get_start_date(date_posted)
    query = """SELECT * FROM jobs"""
    count_query = """SELECT count(*) FROM jobs"""
    filter_query = ""
    params = []

    # Add keyword search if keyword is set
    if (keyword!=None and keyword!=''):
        if(filter_query==""): filter_query += " WHERE "
        filter_query += f"(title LIKE %s OR description LIKE %s) "
        params.append(f'%{keyword}%')
        params.append(f'%{keyword}%')

    # Add location filter if location is set
    if (location!=None and location!=''):
        if(filter_query==""): filter_query += " WHERE "
        else: filter_query += " AND "
        filter_query += f"(country = %s) "
        params.append(f'%{location}%')

    # Add date filter if start_date is set
    if (start_date!=None and start_date!=''):
        start_date_str = start_date.strftime('%Y-%m-%d')
        print(start_date_str)
        filter_query += f" AND (STR_TO_DATE(date_posted, '%%Y-%%m-%%d') > %s)"
        params.append({start_date_str})

    # Add LIMIT and OFFSET directly to the query sring (not as parameters)
    if(page!=None and elements_to_display!=None):
        filter_query += f" LIMIT {elements_to_display} OFFSET {offset}"

    try:
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        params = tuple(params)

        # Execute the main query with parameters correctly
        cursor.execute((query+filter_query), params)
        results = cursor.fetchall()

        cursor.execute((count_query+filter_query), params)
        count = cursor.fetchall()[0]['count(*)']

        # Prepare paginated response
        page_info = {
            'data': pd.DataFrame(results),
            'total': count,
            'number_of_pages': math.ceil(count / elements_to_display) if elements_to_display!= None else None,
            'current_page': page,
            'results_per_page': elements_to_display if page else None
        }
        print(page_info['total'])
        return page_info
    finally:
        connection.close()


def get_jobs_with_sponsorship(keyword, location, date_posted, page, elements_to_display=50):
    connection = get_db_connection()
    if(elements_to_display!= None and page!=None):
        offset = (page - 1) * elements_to_display
    # Default to wildcard if empty
    keyword = keyword if keyword else ''
    location = location if location else ''
    start_date = get_start_date(date_posted)
    query = """SELECT * FROM jobs WHERE sponsorship_provided = 'sponsorship provided' """
    count_query = """SELECT count(*) FROM jobs WHERE sponsorship_provided = 'sponsorship provided' """
    filter_query = ""
    params = []

    # Add keyword search if keyword is set
    if (keyword!=None and keyword!=''):
        filter_query += f" AND (title LIKE %s OR description LIKE %s) "
        params.append(f'%{keyword}%')
        params.append(f'%{keyword}%')

    # Add location filter if location is set
    if (location!=None and location!=''):
        filter_query += f" AND (country LIKE %s) "
        params.append(f'%{location}%')

    # Add date filter if start_date is set
    if (start_date!=None and start_date!=''):
        start_date_str = start_date.strftime('%Y-%m-%d')
        filter_query += f" AND (STR_TO_DATE(date_posted, '%%Y-%%m-%%d') > %s)"
        params.append({start_date_str})

    # Add LIMIT and OFFSET directly to the query sring (not as parameters)
    if(page!=None and elements_to_display!=None):
        filter_query += f" LIMIT {elements_to_display} OFFSET {offset}"

    try:
        cursor = connection.cursor(MySQLdb.cursors.DictCursor)
        params = tuple(params)

        # Execute the main query with parameters correctly
        cursor.execute((query+filter_query), params)
        results = cursor.fetchall()

        cursor.execute((count_query+filter_query), params)
        count = cursor.fetchall()[0]['count(*)']

        # Prepare paginated response
        page_info = {
            'data': pd.DataFrame(results),
            'total': count,
            'number_of_pages': math.ceil(count / elements_to_display) if elements_to_display!= None else None,
            'current_page': page,
            'results_per_page': elements_to_display if page else None
        }
        print(page_info['total'])
        return page_info
    finally:
        connection.close()

# (get_jobs(None, 'Qatar', None, 1, 50 ))