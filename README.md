# Job Sponsorship Predictor

A full-stack web application that automatically scrapes job listings, predicts visa sponsorship likelihood using a trained machine learning model, and presents filtered results on a user-friendly Angular frontend.

## Live Demo

- **Frontend:** Hosted on [GitHub Pages](https://your-username.github.io/your-repo-name)
- **Backend API:** Hosted on [Railway](https://railway.app)

## Features

- Automatically scrapes job listings every 24 hours using [JobSpy](https://pypi.org/project/jobspy/)
- Uses a trained text classification model to predict sponsorship likelihood
- Stores job data in a MySQL database
- Deletes jobs older than 3 months daily
- Search and filter by keyword, location, and job posting duration
- Clean and fast frontend using Angular
- REST API built with Flask

## Data Collection and Labeling

- **Data Scraping**: Job listings were scraped using the [JobSpy](https://pypi.org/project/jobspy/) Python package.
- **Labeling Tool**: A custom labeling interface was built using Flask (with both frontend and backend components) to manually annotate job listings for visa sponsorship status. These labeled examples were used to train the prediction model.

## Tech Stack

- **Frontend:** Angular, TypeScript, GitHub Pages
- **Backend:** Flask, Python, Railway
- **Machine Learning:** Scikit-learn model (trained using job descriptions)
- **Database:** MySQL
- **Scraping:** JobSpy

## Getting Started

### Backend

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name/backend
2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
3. **Set Environment Variables**
   ```bash
   MYSQL_USER=your_user
   MYSQL_PASSWORD=your_password
   MYSQL_HOST=your_host
   MYSQL_DB=your_db
4. **Run the Flask Server**
   ```bash
   flask run

### Frontend

1. **Navigate to the frontend directory**

   ```bash
    cd ../frontend

2. **Install dependencies**

    ```bash
    npm install

3. **Update the backend API URL in environment.ts**

4. **Build and deploy to GitHub Pages**

    ```bash
    ng build --configuration production
    npx angular-cli-ghpages --dir=dist/your-project-name

## Model Training
The machine learning model was trained in two notebooks:

  - **data-exploration.ipynb** – for preprocessing and feature analysis
  
  - **text_classification_model.ipynb** – for model training and evaluation

The model predicts whether a job description implies visa sponsorship based on keywords and textual features.

## Automation Tasks

 - **Daily scraping & inference:** Using a scheduler or cron, the backend:
  
- Fetches new jobs via JobSpy
  
- Applies the ML model to predict sponsorship
  
- Stores the results in the MySQL DB
  
- **Daily cleanup:** Jobs older than 3 months are automatically removed

