import streamlit as st
from data_base import hash_password

# Function to display login form
def display_login(c):
    st.title('Login')
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')

    if st.button('Login'):
        hashed_password = hash_password(password)
        c.execute('SELECT * FROM Users WHERE username = ? AND password = ?', (username, hashed_password))
        user = c.fetchone()

        if user:
            st.session_state.logged_in = True
            st.session_state.user_id = user[0]
            st.success('Logged in successfully')
            st.experimental_rerun()
        else:
            st.error('Invalid username or password')

# Function to display registration form
def display_register(c):
    st.title('Register')
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    confirm_password = st.text_input('Confirm Password', type='password')

    if st.button('Register'):
        c.execute('SELECT * FROM Users WHERE username = ?', (username,))
        existing_user = c.fetchone()
        if existing_user:
            st.error('Username already exists')
        elif password == confirm_password:
            hashed_password = hash_password(password)
            c.execute('INSERT INTO Users (username, password) VALUES (?, ?)', (username, hashed_password))
            c.connection.commit()
            st.success('Registered successfully')
            st.session_state.logged_in = True
            st.session_state.user_id = c.lastrowid
            st.experimental_rerun()
        else:
            st.error('Password does not match')

