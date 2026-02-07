import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def connect_to_database():
    try:
        connection = psycopg2.connect(
            os.getenv('DATABASE_URL')
        )
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