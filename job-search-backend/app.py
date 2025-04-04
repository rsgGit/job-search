from flask import Flask, jsonify, request
from flask_cors import CORS
import pickle
from jobspy import scrape_jobs
import csv
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
nltk.download('wordnet')
from nltk.corpus import wordnet
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import concurrent.futures
from Job_Scraper import get_jobs
import asyncio
import aiohttp

CLEANR = re.compile(r'<\s*.*?\s*>')

app = Flask(__name__)
CORS(app)

@app.route('/hello', methods=['GET'])
def home():
    return jsonify(messsage="Hello, Flask!")


async def get_predictions(data):
    data = format_data(data)
    features = get_features(data, vectorizer)
    predictions = await asyncio.to_thread(model.predict, features)  # Runs in a separate thread
    data['predictions'] = predictions
    return data


async def get_predictions_for_all_data(data):
    loop = asyncio.get_running_loop()
    n =100
    subdata = [data[i:i + n] for i in range(0, len(data), n)]
    tasks = [
        get_predictions(sd)
        for sd in subdata
    ]
    r = await asyncio.gather(*tasks) 
    return pd.concat(r, ignore_index=True)

@app.route('/load-jobs', methods=['GET'])
def load_jobs():
    # timeout = aiohttp.ClientTimeout(total=60)
    keyword = request.args.get('keyword', default="", type=str)
    location = request.args.get('location', default=None, type=str)
    date_posted = request.args.get('date_posted', default=None, type=str)
    if keyword=="": keyword = None
    if location=="": location = None
    if date_posted=="": date_posted = None
    data = asyncio.run(get_jobs(keyword, location, date_posted)) 
    print("scraped")
    data = asyncio.run(get_predictions_for_all_data(data))
    print("processed")
    # final = data[['description', 'processed_description', 'predictions']].copy()
    data['location'] = [None if pd.isna(x) else x for x in data['location']]
    roles_that_provide_sponsorship = data[data["predictions"]==1].to_dict(orient='records')

    return (jsonify(data.to_dict(orient='records')))




def scrape_jobs_from_website(website):
    jobs = scrape_jobs(
            # site_name=['indeed', 'linkedin', 'glassdoor'],
            site_name=[website],
            search_term = "sponsorship",
            google_search_term = "sponsorship",
            # location = "United Kingdom",
            results_wanted = 50,
            linkedin_fetch_description=False,
            hours_old = 24,
            # country_indeed = "United Kingdom"
    )
    return jobs


def clean_text(text):
    
    text = re.sub(CLEANR, '', text)

    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & Pictographs
        "\U0001F680-\U0001F6FF"  # Transport & Map Symbols
        "\U0001F700-\U0001F77F"  # Alchemical Symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"  # Enclosed Characters
        "]+",
        flags=re.UNICODE,
    )
    
    text = emoji_pattern.sub(r"", text) # Remove emojis

    text = re.sub(r"[^A-Za-z0-9\s.!?\'\"]", "", text)  # Keep alphanumeric, spaces, and certain punctuation, excluding '-'
    text = re.sub(r"[\"']", "", text)  # Remove quotes
    text = re.sub(r'\s+', ' ', text).strip()  # Replace multiple spaces with a single space and trim

    return text

def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('VB'):
        return wordnet.VERB
    elif treebank_tag.startswith('NN'):
        return wordnet.NOUN
    elif treebank_tag.startswith('JJ'):
        return wordnet.ADJ
    else:
        return wordnet.NOUN  

def get_lemmatized_words(sentence):
    tokens = word_tokenize(sentence)
    pos_tags = pos_tag(tokens)
    lemmatizer = WordNetLemmatizer()
    lemmatized_words = []
    for word, tag in pos_tags:
        wordnet_pos = get_wordnet_pos(tag)
        lemmatized_word = lemmatizer.lemmatize(word, wordnet_pos)
        lemmatized_words.append(lemmatized_word)
    return lemmatized_words

def format_data(data):

    data = data[['id', 'site', 'job_url', 'title', 'company', 'location', 'date_posted', 'description']].copy()
    data['description'] = data['description'].fillna("")

    data['processed_description'] = data['description'].apply(clean_text)
    data.loc[:, 'processed_description'] = data['processed_description'].str.lower()
    data.loc[:, 'processed_description'] = data['description'].apply(lambda text: ' '.join(get_lemmatized_words(text)))

    custom_stopwords = [
        "job", "position", "role", "team", "company", "candidate", "candidates", "applicant", 
        "hiring", "opportunity", "join", "apply", "skills", "experience", "passionate",
        "environment", "responsibilities", "tasks", "benefits", "qualifications", "qualified", "qualify",
        "including", "preferred", "working", "please", "learning", "scientist", "colleague", "colleagues",
        "highly", "welcome", "successful", "individuals", "exciting", "customer", "design", "product",
        "professional", "solutions", "drive", "growth", "business", "development", "store", "days",
        "organization", "value", "process", "support", "using", "help", "create", "looking", "opportunities", "teams", "encourage",
        "ensure", "must", "make", "meet", "collaborate", "applications", "technical", "data", "including", "develop", "solution", "application",
    ]
    stop_words = set(custom_stopwords)
    
    data.loc[:, 'processed_description'] = data['processed_description'].apply(
        lambda text: ' '.join([word for word in word_tokenize(text) if word not in stop_words])
    )
    data.loc[:, 'processed_description'] = data['processed_description'].apply(
        lambda text: ' '.join([word for word, pos in pos_tag(word_tokenize(text)) if pos not in ['JJ', 'JJR', 'JJS']])
    )

    return data

def get_features(data, vectorizer):
    description_features = vectorizer.transform(data['processed_description'])
    return description_features

def load_model_and_vectorizer():
    model = pickle.load(open("../notebooks/model", 'rb'))
    vectorizer = pickle.load(open("../notebooks/vectorizer", 'rb'))
    return model, vectorizer

model, vectorizer = load_model_and_vectorizer()
