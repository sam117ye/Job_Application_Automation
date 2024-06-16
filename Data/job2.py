# Import dependencies
import requests
from bs4 import BeautifulSoup
import pandas as pd
import random
import os


# Define the job title and location
title = "Application developer"  # Job title
location = "Switzerland"  # Job location
results_per_page = 25 # Number of results per page



# Initialize an empty list to store job information
job_list = []

# Function to get job IDs from a single page
def get_job_ids(page_number, title, location):
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

        # Extracting Employment type and Seniority level accurately
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

# Loop through a specified number of pages (adjust the range as needed)
for page_number in range(10):  # Change 10 to the number of pages you want to scrape
    id_list = get_job_ids(page_number, title, location)
    
    for job_id in id_list:
        job_details = get_job_details(job_id)
        if job_details:
            job_list.append(job_details)

# Create a pandas DataFrame using the list of job dictionaries 'job_list'
jobs_df = pd.DataFrame(job_list)

# Save data to CSV file
jobs_df.to_csv('items2.csv', mode='a', index=False, header=False)