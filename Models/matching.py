from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
import csv
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Embedding, Flatten, concatenate, TextVectorization
from tensorflow.keras.utils import to_categorical

def main():
    # Load the dataset
    filename = '../Data/items2.csv'
    title, location, seniority_level, employment_type, description = load_data(filename)

    # Create a DataFrame
    data = pd.DataFrame({
        'job_title': title,
        'company_location': location,
        'seniority_level': seniority_level,
        'employment_type': employment_type,
        'job_description': description
    })

    # Preprocess the data
    data.dropna(inplace=True)

    # Encode categorical variables
    label_encoders = {}
    for column in ['company_location', 'seniority_level', 'employment_type']:
        le = LabelEncoder()
        data[column] = le.fit_transform(data[column])
        label_encoders[column] = le

    # Encode job description
    vectorizer = TfidfVectorizer()
    data['job_description'] = vectorizer.fit_transform(data['job_description'])
    


    # Encode the target variable
    target_encoder = LabelEncoder()
    data['job_title'] = target_encoder.fit_transform(data['job_title'])

    # Split the dataset
    X = data[['job_description', 'company_location', 'seniority_level', 'employment_type']]
    y = data['job_title']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Standardize numerical features if any (not needed here but left as a placeholder)
    y_train = to_categorical(y_train, num_classes=len(target_encoder.classes_))
    y_test = to_categorical(y_test, num_classes=len(target_encoder.classes_))

    # Create and train the model
    model = create_model(X_train, label_encoders, target_encoder)
    model = train_model(model, X_train, y_train, X_test, y_test)

    # Get user input
    user_input = users_input()

    # Predict the job title
    predicted_job_title = predict_job_title(model, user_input, label_encoders, target_encoder)
    print(f"The predicted job title is: {predicted_job_title}")

def load_data(filename):
    import csv
    # Load the data
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)

        title = []
        descriptions = []

        for row in reader:
            title.append(row[0])
            description.append([str(row[2]), str(row[3]), str(row[4]), str(row[5])])

    return title, description

def create_model(input_shapes, label_encoders, target_encoder):
    job_description_input = Input(shape=(1,), dtype=tf.string, name='job_description')
    company_location_input = Input(shape=(1,), name='company_location')
    seniority_level_input = Input(shape=(1,), name='seniority_level')
    employment_type_input = Input(shape=(1,), name='employment_type')

    # Text Vectorization layer
    vectorizer = TextVectorization(output_sequence_length=100, max_tokens=5000)
    vectorizer.adapt(input_shapes['job_description'])

    # Process text input
    job_description_vectorized = vectorizer(job_description_input)
    embedding_dim = 50
    job_description_embedding = Embedding(input_dim=5000, output_dim=embedding_dim)(job_description_vectorized)
    job_description_flattened = Flatten()(job_description_embedding)

    # Process categorical inputs
    company_location_embedding = Embedding(input_dim=len(label_encoders['company_location'].classes_), output_dim=10)(company_location_input)
    seniority_level_embedding = Embedding(input_dim=len(label_encoders['seniority_level'].classes_), output_dim=10)(seniority_level_input)
    employment_type_embedding = Embedding(input_dim=len(label_encoders['employment_type'].classes_), output_dim=10)(employment_type_input)

    company_location_flattened = Flatten()(company_location_embedding)
    seniority_level_flattened = Flatten()(seniority_level_embedding)
    employment_type_flattened = Flatten()(employment_type_embedding)

    # Concatenate all inputs
    concat_layer = concatenate([job_description_flattened, company_location_flattened, seniority_level_flattened, employment_type_flattened])

    # Add fully connected layers
    dense_layer = Dense(128, activation='relu')(concat_layer)
    output_layer = Dense(len(target_encoder.classes_), activation='softmax')(dense_layer)

    # Define the model
    model = Model(inputs=[job_description_input, company_location_input, seniority_level_input, employment_type_input], outputs=output_layer)

    # Compile the model
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    model.summary()
    return model

def train_model(X_train, y_train, X_test, y_test):

    # Prepare the inputs for the model
    train_inputs = {
        'job_description': X_train['job_description'],
        'company_location': X_train['company_location'],
        'seniority_level': X_train['seniority_level'],
        'employment_type': X_train['employment_type']
    }

    test_inputs = {
        'job_description': X_test['job_description'],
        'company_location': X_test['company_location'],
        'seniority_level': X_test['seniority_level'],
        'employment_type': X_test['employment_type']
    }

    # Train the model
    model.fit(train_inputs, y_train, epochs=10, batch_size=32, validation_data=(test_inputs, y_test))
    
    return model

def users_input():
    job_title = input("job title: ")
    location = input("location: ")
    seniority_level = input("seniority level: ")
    employment_type = input("employment type: ")
    job_description = input("job_description: ")

    ' save the data in a dictionary '
    job_post = {
        "job_title": job_title,
        "company_location": location,
        "seniority_level": seniority_level,
        "employment_type": employment_type,
        "job_description": job_description
    }
    
    return job_post

def predict_job_title(user_input):
    # Encode user input
    user_input['company_location'] = label_encoders['company_location'].transform([user_input['company_location']])[0]
    user_input['seniority_level'] = label_encoders['seniority_level'].transform([user_input['seniority_level']])[0]
    user_input['employment_type'] = label_encoders['employment_type'].transform([user_input['employment_type']])[0]
    
    # Prepare input for prediction
    input_data = {
        'job_description': [user_input['job_description']],
        'company_location': [user_input['company_location']],
        'seniority_level': [user_input['seniority_level']],
        'employment_type': [user_input['employment_type']]
    }
    
    # Predict job title
    prediction = model.predict(user_input())
    predicted_job_title = target_encoder.inverse_transform([prediction.argmax()])[0]
    return predicted_job_title


if __name__ == "__main__":
    main()

