import csv

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

from keras.models import Sequential
from keras.layers import Dense
import openai

# Load the dataset
filename = 'items22.csv'
with open(filename, 'r') as file:
    reader = csv.reader(file)
    next(reader)

    evidence = []
    label = []

    for row in reader:
        evidence.append([row[1], row[2], row[3], row[4], row[5]])  # Include company name
        label.append(row[0])

# Create a DataFrame
data = pd.DataFrame(evidence, columns=['company_name', 'company_location', 'seniority_level', 'employment_type', 'job_description'])
data['job_title'] = label

# Drop any missing values
data.dropna(inplace=True)

# Encode categorical variables
label_encoders = {}
for column in ['company_location', 'seniority_level', 'employment_type']:
    le = LabelEncoder()
    data[column] = le.fit_transform(data[column])
    label_encoders[column] = le

# Encode the target variable
target_encoder = LabelEncoder()
data['job_title'] = target_encoder.fit_transform(data['job_title'])


# Function to get GPT embeddings for job descriptions
openai.api_key = "API_KEY"

def get_gpt_embedding(text, model="text-embedding-3-small"):
   text = text.replace("\n", " ")
   return openai.embeddings.create(input = [text], model=model).data[0].embedding

# Get GPT embeddings for job descriptions
embeddings = data['job_description'].apply(get_gpt_embedding)
embeddings = np.array(embeddings.tolist())

# Combine the categorical features with the GPT embeddings
X_combined = np.hstack([
    data[['company_location', 'seniority_level', 'employment_type']].values,
    embeddings
])

Y = data['job_title'].values


# Split the data into training, validation, and test sets
X_train, X_temp, Y_train, Y_temp = train_test_split(X_combined, Y, test_size=0.3, random_state=42)
X_val, X_test, Y_val, Y_test = train_test_split(X_temp, Y_temp, test_size=0.5, random_state=42)

# Build the neural network model
model = Sequential()
model.add(Dense(256, input_dim=X_combined.shape[1], activation='relu'))
model.add(Dense(128, activation='relu'))
model.add(Dense(len(data['job_title'].unique()), activation='softmax'))

# Compile the model
model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Train the model with validation data
model.fit(X_train, Y_train, epochs=30, batch_size=32, verbose=2, validation_data=(X_val, Y_val))

# Evaluate the model
score, acc = model.evaluate(X_test, Y_test, verbose=2, batch_size=32)
print("Test score: %.2f" % (score))
print("Test accuracy: %.2f" % (acc))

# Example prediction
company_location = 'Switzerland'
seniority_level = 'Mid-Senior level'
employment_type = 'Part-time'
job_description = 'I have a ML and AI Degree from University of Applied Sceinces Lucern. I have experince working with big data sets and in addition, i additional skills of Programming languges like Python, Sql.'


# Encode the categorical inputs
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

print("Top 10 Predicted Job Titles:")
for i in range(10):
    job_title = top_10_job_titles[i]
    prob = top_10_probabilities[i]
    row = data[data['job_title'] == target_encoder.transform([job_title])[0]].iloc[0]
    print(f"{i+1}. {job_title}: {prob:.4f}")
    print(f"   Company Location: {label_encoders['company_location'].inverse_transform([row['company_location']])[0]}")
    print(f"   Seniority Level: {label_encoders['seniority_level'].inverse_transform([row['seniority_level']])[0]}")
    print(f"   Employment Type: {label_encoders['employment_type'].inverse_transform([row['employment_type']])[0]}")
    print(f"   Job Description: {row['job_description']}\n")