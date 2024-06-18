import unittest
from unittest.mock import patch, mock_open, MagicMock
import pickle
import pandas as pd
import numpy as np

# Import the functions to test
from load import load_files, get_gpt_embedding

class TestLoadFunctions(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open)
    @patch('pickle.load')
    @patch('keras.models.load_model')
    def test_load_files(self, mock_load_model, mock_pickle_load, mock_open):
        # Mock data to return
        mock_saved_files = {
            'model_file': 'job_prediction_model.h5',
            'label_encoders': 'label_encoders.pickle',
            'target_encoder': 'target_encoder.pickle',
            'data': {'col1': [1, 2], 'col2': [3, 4]},
            'prediction_results': 'prediction_results.pickle'
        }
        
        # Mock the contents of the individual pickle files
        mock_label_encoders = {'encoder1': MagicMock()}
        mock_target_encoder = MagicMock()
        mock_prediction_results = [0.1, 0.9]
        
        # Set the side effect of mock_pickle_load to return appropriate mock data
        mock_pickle_load.side_effect = [mock_saved_files, mock_label_encoders, mock_target_encoder, mock_prediction_results]
        
        # Mock the model loading
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model
        
        # Call the function
        model, label_encoders, target_encoder, data, prediction_results = load_files()

        # Assertions to ensure the function is working correctly
        mock_open.assert_any_call('model.h5', 'rb')
        mock_open.assert_any_call('label_encoders.pickle', 'rb')
        mock_open.assert_any_call('target_encoder.pickle', 'rb')
        
        self.assertEqual(model, mock_model)
        self.assertEqual(label_encoders, mock_label_encoders)
        self.assertEqual(target_encoder, mock_target_encoder)
        self.assertTrue(np.array_equal(data.values, pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]}).values))
        self.assertEqual(prediction_results, mock_prediction_results)
        
    @patch('openai.Embedding.create')
    def test_get_gpt_embedding(self, mock_openai_embedding_create):
        # Mock response from OpenAI API
        mock_embedding = {'data': [{'embedding': [0.1, 0.2, 0.3]}]}
        mock_openai_embedding_create.return_value = mock_embedding
        
        # Call the function
        text = "Sample job description"
        embedding = get_gpt_embedding(text)
        
        # Assertions to ensure the function is working correctly
        mock_openai_embedding_create.assert_called_once_with(input=[text.replace("\n", " ")], model="text-embedding-ada-002")
        self.assertEqual(embedding, [0.1, 0.2, 0.3])

if __name__ == '__main__':
    unittest.main()
