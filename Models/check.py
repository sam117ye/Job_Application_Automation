import pandas as pd
import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

def main():

    file_path = '../Data/items2.csv'
    evidence, labels = load_data(file_path)

    data, label_encoders, target_encoder = preprocess_data(evidence, labels)

    tokenizer = Tokenizer(num_words=5000, oov_token='<OOV>')
    tokenizer.fit_on_texts(data['job_description'].values)
    max_len = max(data['job_description'].apply(lambda x: len(x.split())))

    Z = preprocess_description(tokenizer, data['job_description'].values, max_len)
    X = np.hstack([data[['company_location', 'seniority_level', 'employment_type']].values, Z])
    Y = data['job_title'].values

    # Split the data into training, validation, and test sets
    X_train, X_temp, Y_train, Y_temp = train_test_split(X, Y, test_size=0.3, random_state=42)
    X_val, X_test, Y_val, Y_test = train_test_split(X_temp, Y_temp, test_size=0.5, random_state=42)

    model = train_model(data, target_encoder, label_encoders, X_train, Y_train, X_val, Y_val)

    # Evaluate the model
    score, acc = model.evaluate(X_test, Y_test, verbose=2, batch_size=32)
    print("Test score: %.2f" % (score))
    print("Test accuracy: %.2f" % (acc))


def load_data(file_path):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)

        evidence = []
        label = []

        for row in reader:
            evidence.append([row[2], row[3], row[4], row[5]])
            label.append(row[0])

    return evidence, label


def preprocess_data(evidence, labels):
    data = pd.DataFrame(evidence, columns=['company_location', 'seniority_level', 'employment_type', 'job_description'])
    data['job_title'] = labels

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

    return data, label_encoders, target_encoder


def preprocess_description(tokenizer, descriptions, max_len):
    sequences = tokenizer.texts_to_sequences(descriptions)
    padded_sequences = pad_sequences(sequences, maxlen=max_len)
    return padded_sequences

def train_model(data, target_encoder, label_encoder, padded_sequences):

    model = sequential()
    model.add(Embedding(5000, 256, input_length=label_encoders.shaper[1]))
    model.add(LSTM(256, dropout=0.1, recurrent_dropout=0.1))
    model.add(Dense(len(data['job_title'].unique()), activation='softmax'))

    # Compile the model
    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.fit(padded_sequences, label_encoder, target_encoder, epochs=10, batch_size=32, verbose=1)

    return model

