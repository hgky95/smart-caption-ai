from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import os
import logging

load_dotenv()

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host = os.getenv('DB_HOST'),
            database = os.getenv('DB_NAME'),
            user = os.getenv('DB_USER'),
            password = os.getenv('DB_PASSWORD'),
            port = os.getenv('DB_PORT')
        )
        return connection
    except Error as e:
        logging.error("Error connecting to MySQL: %s", e)
        raise Error(f"Error connecting to MySQL: {e}")