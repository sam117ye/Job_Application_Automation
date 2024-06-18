import unittest
from unittest.mock import patch, MagicMock
import streamlit as st
from authentication import display_login, display_register

class TestAuthentication(unittest.TestCase):

    @patch('authentication.hash_password')
    @patch('authentication.st.experimental_rerun')
    @patch('authentication.st.success')
    @patch('authentication.st.error')
    @patch('authentication.st.button')
    @patch('authentication.st.text_input')
    def test_display_login(self, mock_text_input, mock_button, mock_error, mock_success, mock_experimental_rerun, mock_hash_password):
        # Mock Streamlit components
        mock_text_input.side_effect = ['test_user', 'test_pass']
        mock_button.return_value = True
        mock_hash_password.return_value = 'hashed_test_pass'
        
        # Mock database cursor
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1, 'test_user', 'hashed_test_pass')

        # Mock session state
        st.session_state = {}

        # Call the function
        display_login(mock_cursor)

        # Assertions
        mock_cursor.execute.assert_called_once_with(
            'SELECT * FROM Users WHERE username = ? AND password = ?', 
            ('test_user', 'hashed_test_pass')
        )
        mock_success.assert_called_once_with('Logged in successfully')
        self.assertTrue(st.session_state['logged_in'])
        self.assertEqual(st.session_state['user_id'], 1)
        mock_experimental_rerun.assert_called_once()

    @patch('authentication.hash_password')
    @patch('authentication.st.experimental_rerun')
    @patch('authentication.st.success')
    @patch('authentication.st.error')
    @patch('authentication.st.button')
    @patch('authentication.st.text_input')
    def test_display_register(self, mock_text_input, mock_button, mock_error, mock_success, mock_experimental_rerun, mock_hash_password):
        # Mock Streamlit components
        mock_text_input.side_effect = ['test_user', 'test_pass', 'test_pass']
        mock_button.return_value = True
        mock_hash_password.return_value = 'hashed_test_pass'

        # Mock database cursor
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None  # Simulate no existing user

        # Mock session state
        st.session_state = {}

        # Call the function
        display_register(mock_cursor)

        # Assertions
        mock_cursor.execute.assert_any_call('SELECT * FROM Users WHERE username = ?', ('test_user',))
        mock_cursor.execute.assert_any_call(
            'INSERT INTO Users (username, password) VALUES (?, ?)', 
            ('test_user', 'hashed_test_pass')
        )
        mock_success.assert_called_once_with('Registered successfully')
        self.assertTrue(st.session_state['logged_in'])
        self.assertEqual(st.session_state['user_id'], mock_cursor.lastrowid)
        mock_experimental_rerun.assert_called_once()

    @patch('authentication.hash_password')
    @patch('authentication.st.error')
    @patch('authentication.st.button')
    @patch('authentication.st.text_input')
    def test_display_register_existing_user(self, mock_text_input, mock_button, mock_error, mock_hash_password):
        # Mock Streamlit components
        mock_text_input.side_effect = ['test_user', 'test_pass', 'test_pass']
        mock_button.return_value = True

        # Mock database cursor
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1, 'test_user', 'hashed_test_pass')  # Simulate existing user

        # Mock session state
        st.session_state = {}

        # Call the function
        display_register(mock_cursor)

        # Assertions
        mock_cursor.execute.assert_called_once_with('SELECT * FROM Users WHERE username = ?', ('test_user',))
        mock_error.assert_called_once_with('Username already exists')

    @patch('authentication.hash_password')
    @patch('authentication.st.error')
    @patch('authentication.st.button')
    @patch('authentication.st.text_input')
    def test_display_register_password_mismatch(self, mock_text_input, mock_button, mock_error, mock_hash_password):
        # Mock Streamlit components
        mock_text_input.side_effect = ['test_user', 'test_pass', 'wrong_pass']
        mock_button.return_value = True

        # Mock database cursor
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None  # Simulate no existing user

        # Mock session state
        st.session_state = {}

        # Call the function
        display_register(mock_cursor)

        # Assertions
        mock_error.assert_called_once_with('Password does not match')

if __name__ == '__main__':
    unittest.main()


