# Import dependencies
import requests
from bs4 import BeautifulSoup
import pandas as pd
import random
import os


# Define the job title and location
title = "Machine Learning Engineer"  # Job title
location = "Germany"  # Job location
results_per_page = 25  # Number of results per page

"""
# Define the job titles and locations
title = ["Machine Learning Engineer", "Data Engineer", "Business Intelligence Analyst", "Data Architect", "Data Analyst", "Data Scientist", "Data Engineer", "Data An", "Back-end developer", "Cloud/software architect", "Cloud/software developer", "Cloud/software applications engineer", "Cloud system administrator", "Cloud system engineer", "DevOps engineer", "Front-end developer", "Full-stack developer", "Java developer", "Platform engineer", "Release manager", "Reliability engineer", "Software engineer", "Software quality assurance analyst", "UI (user interface) designer", "UX (user experience) designer", "Web develope"]
location = ["London", "Berlin", "Paris", "Rome", "Venice", "Florence", "Amsterdam", "Athens", "Barcelona", "Dublin", "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose", "Geneva", "Zürich", "Basel", "Lusanne", "Bern", "Lucerne"]
results_per_page = 50  # Number of results per page
"""

def load_proxies(url):
    proxies = []
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if the GET request was unsuccessful
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")
    else:
        proxies = response.text.split('\n')
    return proxies

# Initialize an empty list to store job information
job_list = []

# Function to get job IDs from a single page
def get_job_ids(page_number, proxies, title, location):
    start = page_number * results_per_page

    for title in title:
        for location in location:
            list_url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={title}&location={location}&start={start}"
    
    proxy = {'http': random.choice(proxies)}
    response = requests.get(list_url, proxies=proxy)
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

url = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt" 
"""
url = "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc"
"""
proxies = load_proxies(url)

# Function to get job details from job ID
def get_job_details(job_id, proxies):
    job_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
    proxy = {'http': random.choice(proxies)}
    job_response = requests.get(job_url, proxies=proxy)
    
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
    id_list = get_job_ids(page_number, proxies, title, location)
    
    for job_id in id_list:
        job_details = get_job_details(job_id, proxies)
        if job_details:
            job_list.append(job_details)

# Create a pandas DataFrame using the list of job dictionaries 'job_list'
jobs_df = pd.DataFrame(job_list)

# Save data to CSV file
jobs_df.to_csv('items1.csv', mode='a', index=False, header=False)

