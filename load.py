import numpy as np
import openai

from keras.models import load_model

import pickle
import pandas as pd

# Load the saved files and return the model, encoders, data, and prediction results
def load_files():
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

    return model, label_encoders, target_encoder, data, prediction_results

# Function to get GPT embeddings for job descriptions
openai.api_key = "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"

def get_gpt_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    response = openai.Embedding.create(input=[text], model=model)
    return response['data'][0]['embedding']


"""import numpy as np
import openai
from keras.models import load_model

import pickle
import pandas as pd


# Load the saved files and return the model, encoders, data, and prediction results

def load_files():
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

    return model, label_encoders, target_encoder, data, prediction_results

# Function to get GPT embeddings for job descriptions
openai.api_key = "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"

def get_gpt_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    response = openai.Embedding.create(input=[text], model=model)
    return response['data'][0]['embedding']
"""