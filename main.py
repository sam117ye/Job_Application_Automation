import streamlit as st
from streamlit_option_menu import option_menu
import sqlite3
import numpy as np
import openai
from keras.models import load_model
import pickle
import pandas as pd
from fpdf import FPDF
import os

# Load necessary modules and functions
from load import load_files, get_gpt_embedding
from data_base import hash_password, get_db_connection
from authentication import display_login, display_register
from scrappy import get_job_ids, get_job_details

# Session state management
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None

# Load files
model, label_encoders, target_encoder, data, prediction_results = load_files()

# Connect to the SQLite database
conn, c = get_db_connection()

# If user is logged in, show the full sidebar and logout option
if st.session_state.logged_in:
    with st.sidebar:
        selected = option_menu('LinkedIn Job Prediction App',
                               ['Personal Information',
                                'Job Prediction',
                                'Generate Cover Letter', 
                                'Scraper', 
                                'Logout'],
                               menu_icon='hospital-fill',
                               icons=['person-fill', 
                                      'briefcase-fill', 
                                      'card-text', 
                                      'search', 
                                      'box-arrow-right'],
                               default_index=0)
        if selected == 'Logout':
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.experimental_rerun()

else:
    # If user is not logged in, show only the login or register page
    selected = st.selectbox('Select Option', ['Login', 'Register'])
    if selected == 'Login':
        display_login(c)
    elif selected == 'Register':
        display_register(c)

# Main page content based on user selection
if st.session_state.logged_in:
    
    if selected == 'Personal Information':
        st.title('User Information')

        st.write('Personal Information')
        col1, col2, col3, col4, col5 = st.columns(5)

        Full_Name = col1.text_input('Full Name')
        Country = col2.text_input('Country')
        Street = col4.text_input('Street')
        Street_number = col3.text_input('Street Number')
        City = col1.text_input('City')
        State = col3.text_input('State')
        Zip = col1.text_input('Zip')
        Email = col1.text_input('Email')
        Phone = col2.text_input('Phone')

        if st.button('Save'):
            user_id = st.session_state.user_id

            c.execute("INSERT INTO personal (name, country, street, street_number, city, state, zip, email, phone, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (Full_Name, Country, Street, Street_number, City, State, Zip, Email, Phone, user_id))

            conn.commit()
            st.success('User information saved successfully')

        st.title('Information about job preference')

        company_location = st.text_input("Company Location")
        seniority_level = st.text_input("Seniority Level")
        employment_type = st.text_input("Employment Type")
        job_description = st.text_area("Job Description", height=400)

        if st.button('Save Job'):
            user_id = st.session_state.user_id

            c.execute("INSERT INTO Job_preference (company_location_preference, seniority_level_preference, employment_type_preference, job_description_preference, user_id) VALUES (?, ?, ?, ?, ?)",
                      (company_location, seniority_level, employment_type, job_description, user_id))

            conn.commit()
            st.success('Job information saved successfully')

        st.title('More information')

        Education = st.text_area('Education', height=200)
        Experience = st.text_area('Experience', height=200)
        Reason = st.text_area('Reason for applying', height=200)
        closing_statement = st.text_area('Closing Statement', height=200)

        if st.button('Save Experience'):
            user_id = st.session_state.user_id

            c.execute("INSERT INTO Experience (education, experience, reason, closing_statement, user_id) VALUES (?, ?, ?, ?, ?)",
                      (Education, Experience, Reason, closing_statement, user_id))

            conn.commit()
            st.success('Personal experience saved successfully')

    elif selected == 'Job Prediction':
        st.title('Job Prediction')

        if st.button("Predict Job Titles"):
            user_id = st.session_state.user_id
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

    elif selected == 'Generate Cover Letter':
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
                max_tokens=500
            )

            cover_letter_text = response['choices'][0]['text']
            st.write("Generated Cover Letter:")
            st.write(cover_letter_text)

            # Save the cover letter in a PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            for line in cover_letter_text.split('\n'):
                pdf.cell(200, 10, txt=line, ln=True)

            pdf_output = f"cover_letter_{user_name.replace(' ', '_')}.pdf"
            pdf.output(pdf_output)

            # Allow the user to download the PDF
            with open(pdf_output, "rb") as pdf_file:
                PDFbyte = pdf_file.read()
                st.download_button(label="Download PDF", data=PDFbyte, file_name=pdf_output, mime='application/octet-stream')

            # Clean up the temporary PDF file
            os.remove(pdf_output)

    elif selected == 'Scraper':
        st.title('Scraper')
        job_title = st.text_input("Job Title")
        location = st.text_input("Location")
        num_jobs = st.number_input("Number of Jobs to Scrape", min_value=1, step=1, value=10)

        if st.button("Scrape Jobs"):
            job_ids = get_job_ids(job_title, location, num_jobs)
            jobs_data = []

            for job_id in job_ids:
                job_details = get_job_details(job_id)
                jobs_data.append(job_details)

            jobs_df = pd.DataFrame(jobs_data)
            st.write(jobs_df)
            csv = jobs_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", data=csv, file_name="jobs.csv", mime='text/csv')

# Close the database connection
conn.close()


