import unittest
from unittest.mock import patch, MagicMock
import hashlib

# Import the functions to test
from data_base import get_db_connection, create_tables, hash_password

class TestDatabaseFunctions(unittest.TestCase):

    @patch('sqlite3.connect')
    def test_get_db_connection(self, mock_connect):
        # Mock the connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Call the function
        conn, c = get_db_connection()
        
        # Assertions to ensure the function is working correctly
        mock_connect.assert_called_once_with('users.db')
        self.assertEqual(conn, mock_conn)
        self.assertEqual(c, mock_cursor)
    
    @patch('data_base.get_db_connection')
    def test_create_tables(self, mock_get_db_connection):
        # Mock the connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = (mock_conn, mock_cursor)
        
        # Call the function
        create_tables()
        
        # Assertions to ensure tables are created
        expected_calls = [
            '''CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )''',
            '''CREATE TABLE IF NOT EXISTS personal (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                country TEXT NOT NULL,
                street TEXT NOT NULL,
                street_number TEXT NOT NULL,
                city TEXT NOT NULL,
                state TEXT NOT NULL,
                zip TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                user_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES Users(id)
            )''',
            '''CREATE TABLE IF NOT EXISTS Job_preference(
                id INTEGER PRIMARY KEY,
                company_location_preference TEXT NOT NULL,
                seniority_level_preference TEXT NOT NULL,
                employment_type_preference TEXT NOT NULL,
                job_description_preference TEXT NOT NULL,
                user_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES Users(id)
            )''',
            '''CREATE TABLE IF NOT EXISTS Experience(
                id INTEGER PRIMARY KEY,
                education TEXT NOT NULL,
                experience TEXT NOT NULL,
                reason TEXT NOT NULL,
                closing_statement TEXT NOT NULL,
                user_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES Users(id)
            )''',
            '''CREATE TABLE IF NOT EXISTS Predicted_Jobs(
                id INTEGER PRIMARY KEY,
                job_title TEXT NOT NULL,
                company_location TEXT NOT NULL,
                seniority_level TEXT NOT NULL,
                employment_type TEXT NOT NULL,
                job_description TEXT NOT NULL,
                user_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES Users(id)
            )'''
        ]
        
        # Verify that the expected SQL commands were executed
        self.assertEqual(mock_cursor.execute.call_count, len(expected_calls))
        
        # Compare SQL commands without extra whitespace
        for call, expected_call in zip(mock_cursor.execute.call_args_list, expected_calls):
            actual_call = call[0][0].replace('\n', '').replace(' ', '')
            expected_call_cleaned = expected_call.replace('\n', '').replace(' ', '')
            self.assertIn(expected_call_cleaned, actual_call)
        
        # Ensure commit and close were called
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
    
    def test_hash_password(self):
        # Example password
        password = 'securepassword'
        
        # Call the function
        hashed = hash_password(password)
        
        # Expected hash value
        expected_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Assertions to ensure the function is working correctly
        self.assertEqual(hashed, expected_hash)

if __name__ == '__main__':
    unittest.main()
