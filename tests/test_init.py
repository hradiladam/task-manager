# test_init
from src.db_config import connect_to_test_db, connect_to_mysql
import mysql.connector

# Connects to mysql, creates test database and table
def create_test_db():
    try:
        with connect_to_mysql() as connection:  # Connects to mysql | (connection.close() and cursor.close() not needed when using 'with')
            with connection.cursor() as cursor:
                cursor.execute("CREATE DATABASE IF NOT EXISTS test_task_manager") # Creates test database
                connection.commit()

    except mysql.connector.Error as error:
        print(f"\n❌ Error while creating test database: {error}")
        raise

    print("\n✔️  Test database created.")


# Creates test table 
def create_test_table():
    try:
        with connect_to_test_db() as connection:  # Connects to test database
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id INT AUTO_INCREMENT PRIMARY KEY, 
                        title VARCHAR(50) NOT NULL,
                        description TEXT NOT NULL,
                        status ENUM('not started', 'done', 'in progress') NOT NULL DEFAULT 'not started',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        CHECK (CHAR_LENGTH(TRIM(title)) > 0),
                        CHECK (CHAR_LENGTH(TRIM(description)) > 0) 
                    );
                """)
                connection.commit()

    except mysql.connector.Error as error:
        print(f"\n❌ Error while creating test table: {error}")
        raise

    print("\n✔️  Test table created.")


# Deletes test database
def drop_test_db():
    try:
        with connect_to_mysql() as connection: # Connects to mysql
            with connection.cursor() as cursor:
                cursor.execute("DROP DATABASE IF EXISTS test_task_manager")
                connection.commit()

    except mysql.connector.Error as error:
        print(f"\n❌ Error while deleting test database: {error}")
        raise
    
    print("\n✔️  Test database deleted.")


# Deletes test table
def drop_test_table():
    try:
        with connect_to_test_db() as connection:  # Connects to test database
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM tasks") # Deletes test table contents
                connection.commit()

    except mysql.connector.Error as error:
        print(f"\n❌ Error while deleting test table: {error}")
        raise

    print("\n✔️  Test table deleted.")


if __name__ == "__main__":
    create_test_db()
