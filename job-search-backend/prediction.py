import pickle
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')
from nltk.corpus import wordnet
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import concurrent.futures
import asyncio
from db_utils import get_all_jobs, apply_predictions
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import time
from timeit import default_timer
from datetime import datetime

# This executor limits the number of threads at any given time
executor = ThreadPoolExecutor()
lemmatizer = WordNetLemmatizer()
lock = multiprocessing.Lock()
START_TIME = default_timer()
CLEANR = re.compile(r'<\s*.*?\s*>')

def log(msg):
    now = datetime.now().strftime('%H:%M:%S.%f'[:-3])
    print(f"[{now}] {msg}")

async def get_predictions(i, data):
    loop = asyncio.get_event_loop()
    # await asyncio.sleep(5)
    data = await asyncio.to_thread(format_data, data)  # Offload format_data
    features = await asyncio.to_thread(get_features, data, vectorizer)  # Offload get_features
    log(f"Completed processing data for batch {i}")
    # # Offloading the blocking `predict_proba` call to a separate thread
    proba = await loop.run_in_executor(executor, model.predict_proba, features)  # Runs in a separate thread
    proba = pd.DataFrame(proba, columns=model.classes_)

    data.loc[:, 'sponsorship_not_provided_probability'] = proba[0].values
    data.loc[:, 'sponsorship_provided_probability'] = proba[1].values
    data.loc[:, 'sponsorship_uncertain_probability'] = proba[2].values

    data.loc[:, 'sponsorship_provided'] = data[
        ['sponsorship_not_provided_probability',
         'sponsorship_provided_probability',
         'sponsorship_uncertain_probability']
    ].idxmax(axis=1)
    
    data.loc[:, 'sponsorship_provided'] = data['sponsorship_provided'].map({
        'sponsorship_not_provided_probability': 'sponsorship not provided',
        'sponsorship_provided_probability': 'sponsorship provided',
        'sponsorship_uncertain_probability': 'sponsorship uncertain'
    })
    
    log(f"Applied model and calculated probability for batch {i}")
      
    return data

async def get_predictions_and_save_predictions(i, data):
    data = await get_predictions(i, data)
    apply_predictions(data)  # Change to await if apply_predictions is async
    log(f"Saved data for batch {i}")    
    return data


async def get_predictions_for_all_data(data):
    log(f"Started applying prediction.")

    n = 500
    subdata = [data[i:i + n] for i in range(0, len(data), n)]
    semaphore = asyncio.Semaphore(5)  # 👈 limit to 5 concurrent threads (you can change)
    log(f"Started processing for {len(subdata)} batches.")
    # We can use asyncio.gather directly with a limited concurrency approach
    async def limited_get_predictions(i, sd):
        async with semaphore:
            log(f"Processing started for batch {i} with {len(sd)} records")
            return await get_predictions_and_save_predictions(i, sd)

    tasks = [limited_get_predictions(i+1, sd) for i, sd in enumerate(subdata)]
    
    # Run tasks concurrently using asyncio.gather
    r = await asyncio.gather(*tasks)
    return r


async def apply_new_model():
    log("Started applying predictions")
    page_data = get_all_jobs(None, None, None, None, None) 
    log(f"Retrieved {len(page_data['data'])} jobs.")

    jobs = page_data['data']
    
    # Run the get_predictions_for_all_data function using asyncio
    data = await get_predictions_for_all_data(jobs)
    log(f"Completed applying predictions for all {len(page_data['data'])} jobs.")

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
    # try:
    with lock:

        tokens = word_tokenize(sentence)
        pos_tags = pos_tag(tokens)
        lemmatizer.lemmatize('cats')
        lemmatized_words = []
        for word, tag in pos_tags:
            wordnet_pos = get_wordnet_pos(tag)
            lemmatized_word = lemmatizer.lemmatize(word, wordnet_pos)
            lemmatized_words.append(lemmatized_word)
    return lemmatized_words
        # except Exception as e:
        #     print(e)

def format_data(data):
    data = data.copy()
    # data = data[['id', 'site', 'job_url', 'title', 'company', 'location', 'date_posted', 'description']].copy()
    data.loc[:, 'description'] = data['description'].fillna("")

    data.loc[:, 'processed_description'] = data['description'].apply(clean_text)

    data.loc[:, 'processed_description'] = data['processed_description'].str.lower()

    data.loc[:, 'processed_description'] = data['processed_description'].apply(lambda text: ' '.join(get_lemmatized_words(text)))

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
# asyncio.run(apply_new_model())

