# db_config
import os
import mysql.connector
import sys
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

# Database connection configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": os.getenv("DB_PASSWORD") 
}

# Connect to MySQL server without specifying a database
def connect_to_mysql():
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
        )
        return connection
    
    except Error as error:
        print(f"\n❌ Error connecting to MySQL server: {error}")
        sys.exit(1)

# Connect to production database and return connection
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database="task_manager"  # renamed from spravce_ukolu to English equivalent
        )
        return connection
    
    except Error as error:
        print(f"\n❌ Error connecting to the database: {error}")
        sys.exit(1)

# Connect to test database and return connection
# When the test database is created in test_init.py, this config will be reused in test fixtures
def connect_to_test_db():
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database="test_task_manager"  # renamed from testovaci_spravce_ukolu to English equivalent
        )
        return connection
    
    except Error as error:
        print(f"\n❌ Error connecting to the test database: {error}")
        sys.exit(1)
