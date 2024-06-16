from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
import csv
import pandas as pd

import users_input from user

filename = '../Data/items2.csv'

def load_data(filename):
    # Load the data
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)

        data = []

        for row in reader:
            data.append([row[0], row[5]])

    return data

# Load the data
data = load_data(filename)

# Assume 'job_description' is the column with job descriptions and 'job_type' is the column with job types
X = [item[0] for item in data]
y = [item[1] for item in data]

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create a pipeline that first transforms the text data into TF-IDF vectors, then trains a Linear SVC
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('clf', LinearSVC()),
])

# Train the model
pipeline.fit(X_train, y_train)

# Test the model
predictions = pipeline.predict(X_test)

# Print a classification report
print(classification_report(y_test, predictions))

# Now you can use the trained model to predict the job type for a new job description
new_job_description = users_input()
predicted_job_type = pipeline.predict([new_job_description])
print(f"The predicted job type for the new job description is: {predicted_job_type[0]}")


# Import necessary modules
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

# Split the data into training and testing sets for both models
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
y_train_inverse, y_test_inverse, X_train_inverse, X_test_inverse = train_test_split(y, X, test_size=0.2, random_state=42)

# Create a pipeline for the first model (predicting y based on X)
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('clf', LinearSVC()),
])
# Train the first model
pipeline.fit(X_train, y_train)
# Evaluate the first model
y_pred = pipeline.predict(X_test)
print(classification_report(y_test, y_pred))

# Create a pipeline for the second model (predicting X based on y)
pipeline_inverse = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('clf', LinearSVC()),
])
# Train the second model
pipeline_inverse.fit(y_train_inverse, X_train_inverse)
# Evaluate the second model
X_pred_inverse = pipeline_inverse.predict(y_test_inverse)
print(classification_report(X_test_inverse, X_pred_inverse))