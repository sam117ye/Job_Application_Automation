import numpy as np
import openai

from keras.models import load_model

import pickle
import pandas as pd

import os
import pickle
import pandas as pd
from keras.models import load_model

def load_files():
    # Define the directory path
    dir_path = 'Saved_trainnings'
    
    # Load the saved files
    with open(os.path.join(dir_path, 'job_prediction.sav'), 'rb') as handle:
        saved_files = pickle.load(handle)

    # Load the model
    model_path = os.path.join(dir_path, saved_files['model_file'])
    model = load_model(model_path)

    # Load the encoders
    label_encoders_path = os.path.join(dir_path, saved_files['label_encoders'])
    with open(label_encoders_path, 'rb') as handle:
        label_encoders = pickle.load(handle)

    target_encoder_path = os.path.join(dir_path, saved_files['target_encoder'])
    with open(target_encoder_path, 'rb') as handle:
        target_encoder = pickle.load(handle)

    # Load the additional data
    data = pd.DataFrame(saved_files['data'])

    # Load the prediction results
    prediction_results = saved_files['prediction_results']

    return model, label_encoders, target_encoder, data, prediction_results

openai.api_key = "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"


# Function to get GPT embeddings for job descriptions
def get_gpt_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    response = openai.Embedding.create(input=[text], model=model)
    return response['data'][0]['embedding']
