# main
from db_config import connect_to_db
from task_database import TaskDatabase
from task_manager import TaskManager


# Main menu of the application
def main_menu(manager):
    while True:
        print("""\n
            =================== Task Manager - Main Menu ===================
            1. Add task
            2. Show tasks
            3. Update task
            4. Delete task
            5. Exit program
            =================================================================
          """)
    
        choice = input("\nChoose an option (1-5): ")
        
        if choice == "1":
            manager.add_task()
        elif choice == "2":
            manager.show_tasks()  
        elif choice == "3":
            manager.update_task()
        elif choice == "4":
            manager.delete_task()
        elif choice == "5":
            print("\n👋  Program terminated.")
            break 
        else:
            print("\n❗  Invalid choice. Please try again.")


# Create the tasks table in DB and run the main menu
if __name__ == "__main__":
    connection = connect_to_db()
    if connection:
        try:
            db = TaskDatabase(connection)
            db.create_table_db()
            manager = TaskManager(db)
            main_menu(manager)
        finally:
            connection.close()