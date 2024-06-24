# Job Application Automation

This application simplifies job searching and application process by matching users experince and interest with job postings on linkedn.

## Description

This project integrates various technologies including Streamlit for web app development, SQLite for database management, Keras for machine learning model operations, and several others to provide a comprehensive solution for jon application proccess. It includes functionalities such as user authentication, data processing, and job scraping from web sources.

### Dependencies

- Python 3.x
- Streamlit
- SQLite3
- NumPy
- OpenAI
- Keras
- Pandas


### Executing program

- Run the command `streamlit run main.py` to start the web application.
- Navigate to the URL provided by Streamlit in your web browser.

## Files Description

- `main.py`: The entry point of the web application integrating all components.

- `authentication.py`: Manages user authentication processes.

- `load.py`: Contains functions for loading necessary files and models.

- `scrappy.py`: Includes functions for scraping job details from the web.

- `data_base.py`: Handles database connections and operations.

- `Models/`: Directory containing experimental machine learning models.

- `Data/`: Directory for storing data files used by the application.

- `Saved_trainings/`: Contains saved training sessions or results.

- `Unit_test/`: Contains functions to test unit fuctionaly of Used fuctions.

#### Problems to Solve

* User
  - Add option to edit user data

* Scrapping
  - Set-up Proxies for Scrapping
  - debung saving on .csv file

* Prediction Model
  - Predicted input that the model never saw before
  - Improve trainning
  - if job predicted, avoid predicting again.

* Cover letter generation
   - choose better model/Fine tune model
   - improve code to choose for which predicted job to generate for
   - save into a PDF FIle

* Train model automaticlly from new scrapped data
.
