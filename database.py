import psycopg2
import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env file
load_dotenv()

def connect_to_database():
    try:
        # Try to get DATABASE_URL from Streamlit secrets first (for Streamlit Cloud)
        # Fall back to os.getenv for local development
        try:
            database_url = st.secrets["DATABASE_URL"]
        except:
            database_url = os.getenv('DATABASE_URL')
        
        connection = psycopg2.connect(database_url)
        print("Connected to PostgreSQL database successfully!")
        return connection
    except Exception as error:
        print("Error connecting to PostgreSQL database:", error)
        return None
    
if __name__ == "__main__":
    conn = connect_to_database()
    if conn:
        conn.close()
        print("Database connection closed.")