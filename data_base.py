import sqlite3
import hashlib

# Function to connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('Data/users.db')
    c = conn.cursor()
    return conn, c

# Create tables if they don't exist
def create_tables():
    conn, c = get_db_connection()
    
    c.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS personal (
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
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS Job_preference(
        id INTEGER PRIMARY KEY,
        company_location_preference TEXT NOT NULL,
        seniority_level_preference TEXT NOT NULL,
        employment_type_preference TEXT NOT NULL,
        job_description_preference TEXT NOT NULL,
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES Users(id)
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS Experience(
        id INTEGER PRIMARY KEY,
        education TEXT NOT NULL,
        experience TEXT NOT NULL,
        reason TEXT NOT NULL,
        closing_statement TEXT NOT NULL,
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES Users(id)
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS Predicted_Jobs(
        id INTEGER PRIMARY KEY,
        job_title TEXT NOT NULL,
        company_location TEXT NOT NULL,
        seniority_level TEXT NOT NULL,
        employment_type TEXT NOT NULL,
        job_description TEXT NOT NULL,
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES Users(id)
    )
    ''')

    conn.commit()
    conn.close()

# Hash function for passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

