import streamlit as st
from streamlit_option_menu import option_menu
import streamlit_authenticator as stauth

import numpy as np
import openai
from keras.models import load_model
import pickle
import pandas as pd
import sqlite3
from bs4 import BeautifulSoup
import requests
import os

# User authentication

stauth.authenticate()

# Connect to the SQLite database
conn = sqlite3.connect('job_application.db')
c = conn.cursor()

# Create tables if they don't exist
c.execute('''
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    street TEXT NOT NULL,
    street_number TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    zip TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS Job_preference(
    id INTEGER PRIMARY KEY,
    company_location_preference TEXT NOT NULL,
    seniority_level_preference TEXT NOT NULL,
    employment_type_preference TEXT NOT NULL,
    job_description_preference TEXT NOT NULL,
    user_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES Users(id)
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS experience(
    id INTEGER PRIMARY KEY,
    education TEXT NOT NULL,
    experience TEXT NOT NULL,
    reason TEXT NOT NULL,
    closing_statement TEXT NOT NULL,
    user_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES Users(id)
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS Predicted_Jobs(
    id INTEGER PRIMARY KEY,
    job_title TEXT NOT NULL,
    company_location TEXT NOT NULL,
    seniority_level TEXT NOT NULL,
    employment_type TEXT NOT NULL,
    job_description TEXT NOT NULL,
    user_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES Users(id)
)
''')

conn.commit()

# Load the combined file
with open('job_prediction.sav', 'rb') as handle:
    saved_files = pickle.load(handle)

# Load the model
model = load_model(saved_files['model_file'])

# Load the encoders
with open(saved_files['label_encoders'], 'rb') as handle:
    label_encoders = pickle.load(handle)
    
with open(saved_files['target_encoder'], 'rb') as handle:
    target_encoder = pickle.load(handle)

# Load the additional data
data = pd.DataFrame(saved_files['data'])

# Load the prediction results
prediction_results = saved_files['prediction_results']

# Function to get GPT embeddings for job descriptions
openai.api_key = "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"

def get_gpt_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    response = openai.Embedding.create(input=[text], model=model)
    return response['data'][0]['embedding']

# sidebar for navigation
with st.sidebar:
    selected = option_menu('Linkdens Job Prediction App',

                           ['User Information',
                            'Job Prediction',
                            'Generate Cover Letter',
                            'Scraper'],
                           menu_icon='hospital-fill',
                           icons=['person-fill', 'briefcase-fill', 'card-text', 'search'],
                           default_index=0)

if selected == 'User Information':
    st.title('User Information')

    st.write('Personal Information')
    col1, col2, col3, col4, col5 = st.columns(5)

    Full_Name = col1.text_input('Full Name')
    Country = col2.text_input('Country')
    Street = col1.text_input('Street')
    Street_number = col2.text_input('Street Number')
    City = col2.text_input('City')
    State = col3.text_input('State')
    Zip = col4.text_input('Zip')
    Email = col1.text_input('Email')
    Phone = col2.text_input('Phone')

    st.write('Information about job preference')

    company_location = st.text_input("Company Location")
    seniority_level = st.text_input("Seniority Level")
    employment_type = st.text_input("Employment Type")
    job_description = st.text_area("Job Description", height=400)

    st.write('More information')

    Education = st.text_area('Education', height=200)
    Experience = st.text_area('Experience', height=200)
    Reason = st.text_area('Reason for applying', height=200)
    closing_statement = st.text_area('Closing Statement', height=200)

    if st.button('Save user information'):
        c.execute("INSERT INTO Users (name, country, street, street_number, city, state, zip, email, phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (Full_Name, Country, Street, Street_number, City, State, Zip, Email, Phone))
        user_id = c.lastrowid

        c.execute("INSERT INTO Job_preference (company_location_preference, seniority_level_preference, employment_type_preference, job_description_preference, user_id) VALUES (?, ?, ?, ?, ?)",
                  (company_location, seniority_level, employment_type, job_description, user_id))
        conn.commit()

        c.execute("INSERT INTO experience (education, experience, reason, closing_statement, user_id) VALUES (?, ?, ?, ?, ?)",
                  (Education, Experience, Reason, closing_statement, user_id))
        conn.commit()
        st.success('User information saved successfully')

if selected == 'Job Prediction':
    # Streamlit app
    st.title("Job Prediction")

    """
    Input fields
    company_location = st.text_input("Company Location")
    seniority_level = st.text_input("Seniority Level")
    employment_type = st.text_input("Employment Type")
    job_description = st.text_area("Job Description", height=500)"""

    if st.button("Predict Job Titles"):
        user_id = c.execute("SELECT id FROM Users ORDER BY id DESC LIMIT 1").fetchone()[0]
        company_location = c.execute("SELECT company_location_preference FROM Job_preference WHERE user_id=?", (user_id,)).fetchone()[0]
        seniority_level = c.execute("SELECT seniority_level_preference FROM Job_preference WHERE user_id=?", (user_id,)).fetchone()[0]
        employment_type = c.execute("SELECT employment_type_preference FROM Job_preference WHERE user_id=?", (user_id,)).fetchone()[0]
        job_description = c.execute("SELECT job_description_preference FROM Job_preference WHERE user_id=?", (user_id,)).fetchone()[0]

        
        # Encode the categorical inputs

        try:
            encoded_location = label_encoders['company_location'].transform([company_location])[0]
            encoded_seniority = label_encoders['seniority_level'].transform([seniority_level])[0]
            encoded_employment = label_encoders['employment_type'].transform([employment_type])[0]

            # Get GPT embedding for the job description
            encoded_description = get_gpt_embedding(job_description)

            # Combine the inputs
            input_data = np.hstack([[encoded_location, encoded_seniority, encoded_employment], encoded_description]).reshape(1, -1)

            # Predict the job titles
            prediction = model.predict(input_data)

            # Get the top 10 predictions
            top_10_indices = prediction[0].argsort()[-10:][::-1]
            top_10_probabilities = prediction[0][top_10_indices]
            top_10_job_titles = target_encoder.inverse_transform(top_10_indices)

            st.write("Top 10 Predicted Job Titles:")
            for i in range(10):
                job_title = top_10_job_titles[i]
                prob = top_10_probabilities[i]
                row = data[data['job_title'] == target_encoder.transform([job_title])[0]].iloc[0]
                st.write(f"{i+1}. {job_title}: {prob:.4f}")
                st.write(f"   Company Location: {label_encoders['company_location'].inverse_transform([row['company_location']])[0]}")
                st.write(f"   Seniority Level: {label_encoders['seniority_level'].inverse_transform([row['seniority_level']])[0]}")
                st.write(f"   Employment Type: {label_encoders['employment_type'].inverse_transform([row['employment_type']])[0]}")
                st.write(f"   Job Description: {row['job_description']}\n")

                # Save the predicted jobs
                c.execute("INSERT INTO Predicted_Jobs (job_title, company_location, seniority_level, employment_type, job_description, user_id) VALUES (?, ?, ?, ?, ?, ?)",
                          (job_title, row['company_location'], row['seniority_level'], row['employment_type'], row['job_description'], user_id))
                conn.commit()

        except Exception as e:
            st.error(f"An error occurred: {e}")

if selected == 'Generate Cover Letter':
    st.title('Cover Letter Generator')

    # Load job title and company name from the Predicted_Jobs table
    predicted_job = c.execute("SELECT job_title, company_location FROM Predicted_Jobs ORDER BY id DESC LIMIT 1").fetchone()
    if predicted_job:
        job_title, company_name = predicted_job
    else:
        job_title, company_name = "", ""

    st.write("Provide additional details for the cover letter:")

    # Display loaded job title and company name
    st.text_input("Job Title", job_title, disabled=True)
    st.text_input("Company Name", company_name, disabled=True)

    if st.button("Generate Cover Letter"):
        user_id = c.execute("SELECT id FROM Users ORDER BY id DESC LIMIT 1").fetchone()[0]
        user_info = c.execute("SELECT * FROM Users WHERE id=?", (user_id,)).fetchone()
        job_pref = c.execute("SELECT * FROM Job_preference WHERE user_id=?", (user_id,)).fetchone()
        experience = c.execute("SELECT * FROM experience WHERE user_id=?", (user_id,)).fetchone()

        user_name, country, street, street_number, city, state, zip_code, email, phone = user_info[1:]
        company_location, seniority_level, employment_type, job_description = job_pref[1:-1]
        education, user_experience, reason, closing_statement = experience[1:-1]

        cover_letter_prompt = f"""
        Generate an application letter for the position of {job_title} at {company_name}.
        Here is the applicant's information:
        - Name: {user_name}
        - Address: {street} {street_number}, {city}, {state}, {zip_code}, {country}
        - Email: {email}
        - Phone: {phone}
        - Company Location: {company_location}
        - Seniority Level: {seniority_level}
        - Employment Type: {employment_type}
        - Job Description: {job_description}
        - Education: {education}
        - Experience: {user_experience}
        - Reason for applying: {reason}
        - Closing Statement: {closing_statement}
        """

        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=cover_letter_prompt,
            max_tokens=500,
            top_p=0.9,
            frequency_penalty=0,
            presence_penalty=0
        )

        generated_text = response.choices[0].text.strip()
        st.text_area("Generated Cover Letter", value=generated_text, height=400)

        if st.button("Download Cover Letter as PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for line in generated_text.split('\n'):
                pdf.cell(200, 10, txt=line, ln=True)
            pdf_path = os.path.join(os.getcwd(), 'cover_letter.pdf')
            pdf.output(pdf_path)
            st.success(f"Cover letter saved as {pdf_path}")

# Function to get job IDs from a single page
def get_job_ids(page_number, title, location, results_per_page=25):
    start = page_number * results_per_page
    list_url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={title}&location={location}&start={start}"
    response = requests.get(list_url)
    list_data = response.text
    list_soup = BeautifulSoup(list_data, "html.parser")
    page_jobs = list_soup.find_all("li")

    id_list = []
    for job in page_jobs:
        base_card_div = job.find("div", {"class": "base-card"})
        if base_card_div:
            job_id = base_card_div.get("data-entity-urn").split(":")[3]
            id_list.append(job_id)
    return id_list

# Function to get job details from job ID
def get_job_details(job_id):
    job_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
    job_response = requests.get(job_url)
    if job_response.status_code == 200:
        job_soup = BeautifulSoup(job_response.text, "html.parser")
        job_post = {}
        try:
            job_post["job_title"] = job_soup.find("h2", {"class": "top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0 topcard__title"}).text.strip()
        except:
            job_post["job_title"] = None
        try:
            job_post["company_name"] = job_soup.find("a", {"class": "topcard__org-name-link topcard__flavor--black-link"}).text.strip()
        except:
            job_post["company_name"] = None
        try:
            job_post["company_location"] = job_soup.find("span", {"class": "topcard__flavor topcard__flavor--bullet"}).text.strip()
        except:
            job_post["company_location"] = None
        criteria_elements = job_soup.find_all("span", {"class": "description__job-criteria-text"})
        if criteria_elements:
            try:
                job_post["seniority_level"] = criteria_elements[0].text.strip()
            except IndexError:
                job_post["seniority_level"] = None
            try:
                job_post["employment_type"] = criteria_elements[1].text.strip()
            except IndexError:
                job_post["employment_type"] = None
        else:
            job_post["seniority_level"] = None
            job_post["employment_type"] = None
        try:
            job_post["job_description"] = job_soup.find("div", {"class": "show-more-less-html__markup show-more-less-html__markup--clamp-after-5 relative overflow-hidden"}).text.strip()
        except:
            job_post["job_description"] = None
        return job_post
    else:
        return None

if selected == 'Scraper':
    st.title('LinkedIn Job Scraper')

    title = st.text_input('Job Title', 'Application developer')
    location = st.text_input('Location', 'Switzerland')
    pages_to_scrape = st.number_input('Number of Pages to Scrape', min_value=1, max_value=100, value=10)
    results_per_page = st.number_input('Results Per Page', min_value=1, max_value=100, value=25)

    if st.button('Scrape Jobs'):
        job_list = []
        for page_number in range(pages_to_scrape):
            id_list = get_job_ids(page_number, title, location, results_per_page)
            for job_id in id_list:
                job_details = get_job_details(job_id)
                if job_details:
                    job_list.append(job_details)
        if job_list:
            jobs_df = pd.DataFrame(job_list)
            st.write(jobs_df)
            # Save data to CSV file
            csv_path = os.path.join(os.getcwd(), 'scraped_jobs.csv')
            jobs_df.to_csv(csv_path, index=False)
            st.success(f"Scraped data saved to {csv_path}")
        else:
            st.warning("No jobs found or an error occurred during scraping.")

# Close the database connection when the app is stopped

conn.close()
