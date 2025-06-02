import pandas as pd
import ipywidgets as widgets
from IPython.display import display, HTML
import sqlite3
import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

keywordsRelatedToSponsorship = ["sponsorship", "visa", "right to work", "right to stay", "h1b", "h-1b", "authorized to work", "work authorization", "sponsor", "sponsored", "based", "security clearance", "passport", "eligible"]
wordBeingLookedAtIndex = 0

def highlightText(text, wordsToHighlight):
    for word in wordsToHighlight:
        text = text.lower().replace(word, f"<span style='background-color:yellow;'>{word}</span>")
    return text

def fetchDataFromTheDb():
    conn = sqlite3.connect('data/labelled_data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # query = "SELECT * FROM labelled_job_postings WHERE sponsorship_available IS NULL AND (LOWER(title) LIKE ? OR LOWER(description) LIKE ?) limit 1"
    # keyword = "%" + keywordsRelatedToSponsorship[wordBeingLookedAtIndex].lower() + "%"
    # cursor.execute(query, (keyword, keyword))
    query = "SELECT * FROM labelled_job_postings WHERE sponsorship_available IS NULL or sponsorship_available = '' limit 1"
    cursor.execute(query)

    data = cursor.fetchone()
    conn.close()
    if(data): return dict(data)
    else: return None

def saveData(sponsorship_label, id):
    conn = sqlite3.connect("data/labelled_data.db")
    cursor = conn.cursor()
    cursor.execute('''
                        UPDATE labelled_job_postings
                        SET sponsorship_available = ?
                        WHERE id = ?
                   ''', (sponsorship_label, id))
    
    conn.commit()
    conn.close()

def getDataForChart():
    conn = sqlite3.connect('data/labelled_data.db')
    conn.row_factory= sqlite3.Row
    cursor= conn.cursor()
    cursor.execute('''
                        SELECT count(*) FROM labelled_job_postings
                   ''')
    total_data = cursor.fetchone()[0]
    cursor.execute('''
                        SELECT count(*) FROM labelled_job_postings where sponsorship_available is not null and not sponsorship_available = ''
                   ''')
    total_labelled_data = cursor.fetchone()[0]
    cursor.execute('''
                        SELECT count(*) FROM labelled_job_postings where sponsorship_available = 'Uncertain'
                   ''')
    total_uncertain_data = cursor.fetchone()[0]
    cursor.execute('''
                        SELECT count(*) FROM labelled_job_postings where sponsorship_available = 'Sponsorship Provided'
                   ''')
    total_sponsorship_provided_data = cursor.fetchone()[0]
    cursor.execute('''
                        SELECT count(*) FROM labelled_job_postings where sponsorship_available = 'Sponsorship Not Provided'
                   ''')
    total_sponsorship_not_provided_data = cursor.fetchone()[0]
    
    # query = "SELECT count(*) FROM labelled_job_postings WHERE sponsorship_available IS not NULL AND (LOWER(title) LIKE ? OR LOWER(description) LIKE ?)"
    # keyword = "%" + keywordsRelatedToSponsorship[wordBeingLookedAtIndex].lower() + "%"
    # cursor.execute(query, (keyword, keyword))
    # total_labelled_data_with_keyword = cursor.fetchone()[0]

    # query = "SELECT count(*) FROM labelled_job_postings WHERE (LOWER(title) LIKE ? OR LOWER(description) LIKE ?)"
    # keyword = "%" + keywordsRelatedToSponsorship[wordBeingLookedAtIndex].lower() + "%"
    # cursor.execute(query, (keyword, keyword))
    # total_data_with_keyword = cursor.fetchone()[0]

    total_labelled_data_with_keyword = "-"
    total_data_with_keyword = "-"
    # keyword = keywordsRelatedToSponsorship[wordBeingLookedAtIndex]
    keyword = "-"
    return {'totalData':total_data, 'total_labelled_data':total_labelled_data, 'total_uncertain_data':total_uncertain_data, 'total_sponsorship_provided_data':total_sponsorship_provided_data, 'total_sponsorship_not_provided_data':total_sponsorship_not_provided_data, 'keyword':keyword, 'total_labelled_data_with_keyword':total_labelled_data_with_keyword, 'total_data_with_keyword':total_data_with_keyword}

def getCountOfJobsWithKeyword():
    conn = sqlite3.connect('data/labelled_data.db')
    conn.row_factory= sqlite3.Row
    cursor= conn.cursor()
    # query = "SELECT count(*) FROM labelled_job_postings WHERE sponsorship_available IS NULL AND (LOWER(title) LIKE ? OR LOWER(description) LIKE ?)"
    # keyword = "%" + keywordsRelatedToSponsorship[wordBeingLookedAtIndex].lower() + "%"
    # cursor.execute(query, (keyword, keyword))

    query = "SELECT count(*) FROM labelled_job_postings WHERE sponsorship_available IS NULL or sponsorship_available = '' "
    cursor.execute(query)
    count = cursor.fetchone()[0]
    return count

def setKeywordBeingSet():  
    wordBeingLookedAtIndex = 0  
    while(getCountOfJobsWithKeyword()==0 and (wordBeingLookedAtIndex+1)<len(keywordsRelatedToSponsorship)):
        print(wordBeingLookedAtIndex)
        wordBeingLookedAtIndex = wordBeingLookedAtIndex + 1


###############################################################################################
###############################################################################################

@app.route("/")
def index():
    return render_template("data_labelling_ui.html")

@app.route("/get-job")
def get_job():
    data = fetchDataFromTheDb()
    if(data):
        job_data = {
            "id": data["id"],
            "job_posting_id": data["job_posting_id"],
            "title": highlightText(data["title"], keywordsRelatedToSponsorship),
            "company": data["company"],
            "location": data["location"],
            "job_site": data["job_site"],
             "description": highlightText(data["description"], keywordsRelatedToSponsorship),
        }
        return jsonify(job_data)
    else:
        return jsonify({"error": "No more data"})

@app.route("/save-job", methods = ["POST"])
def save_job():
    sponsorship_label = request.json.get("sponsorship_label")
    id = request.json.get("id")
    saveData(sponsorship_label, id)
    return jsonify({"message": "Data saved successfully!"})

@app.route("/get-data-for-chart")
def get_data_for_chart():
    data = getDataForChart()
    return jsonify(data)

###############################################################################################
###############################################################################################

if __name__ == "__main__":
    # setKeywordBeingSet()
    app.run(debug=True)