# task_database
import mysql.connector
from mysql.connector import Error


class TaskDatabase:
    def __init__(self, connection):
        self.connection = connection

    # Creates table in the database "task_manager"
    def create_table_db(self):
        try:
            with self.connection.cursor() as cursor:
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
            self.connection.commit()
        except Error as error:
            print(f"\n❌  Error creating table: {error}")
            raise
    
    # Function to insert a task into the database
    def add_task_db(self, title, description):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("INSERT INTO tasks (title, description) VALUES (%s, %s)", (title, description))
                self.connection.commit()
                
                print(f"\n✅ Task was added with ID: {cursor.lastrowid}")
        except mysql.connector.Error as error:
            print(f"\n❌  Error while adding task: {error}")
            raise

    # Function to load and return all tasks from the database complete
    def fetch_tasks_db(self):
        try: 
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT id, title, description, status, created_at FROM tasks WHERE status IN ('not started', 'in progress')")
                return cursor.fetchall()
        except mysql.connector.Error as error:
            print(f"❌  Error selecting tasks for display: {error}")
            raise
    
    # Helper function to select and return all task IDs and titles from the database  
    def fetch_task_ids_db(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT id, title FROM tasks")
                return cursor.fetchall()
        except mysql.connector.Error as error:
            print(f"❌  Error selecting task IDs: {error}")
            return []

    # Function to update the task status in the database
    def update_task_db(self, task_id, new_status):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("UPDATE tasks SET status = %s WHERE id = %s", (new_status, task_id))
                self.connection.commit()
            return True
        except mysql.connector.Error as error:
            print(f"\n❌  Error updating task: {error}")
            self.connection.rollback()  # rollback to clear failed transaction
            return False

    # Function to delete a task from the database by ID
    def delete_task_db(self, task_id):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
                self.connection.commit()
            
                if cursor.rowcount == 0:
                    # No rows deleted => invalid id
                    return False
                
            return True
        except mysql.connector.Error as error:
            print(f"❌  Error deleting task: {error}")
            return False
