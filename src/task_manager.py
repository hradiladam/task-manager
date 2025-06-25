# task_manager
from utils import normalize_state, validate_task


class TaskManager:
    def __init__(self, db):
        self.db = db

    # Function to create a new task
    def add_task(self):
        while True:
            try:
                title = self.input_or_cancel("\nEnter task title (or 'b' to go back): ")
                description = self.input_or_cancel("Enter task description (or 'b' to go back): ")

                error = validate_task(title, description)
                
                if error:
                    print(f"\n❗ {error} Please try again.\n")
                    continue

                self.db.add_task_db(title, description)
                break

            except OperationCancelled:
                print("\nℹ️  Operation cancelled. Returning to main menu.")
                break
                
            except Exception as error:
                print("Something went wrong: ", error)
                break

    # Function to display tasks to the user
    def show_tasks(self):
        tasks = self.db.fetch_tasks_db()
        
        if not tasks:
            print(f"\n❗ No tasks to display.")
        else:
            for index, task in enumerate(tasks, 1):
                print(f"{index}. ID: {task[0]} | Title: {task[1]} | Description: {task[2]} | Status: {task[3]} | Created: {task[4].strftime('%d.%m.%Y %H:%M')}") 

    # Helper function to select a task ID
    def select_task_id(self):
        tasks = self.db.fetch_task_ids_db()
        
        if not tasks:
            print("\n❗ The task list is empty.")
            return None

        print("\n📋 Task list:")
        for index, (task_id, title) in enumerate(tasks, 1):
            print(f"{index}. ID: {task_id} | Title: {title}")

        valid_ids = {str(task_id) for task_id, _ in tasks}

        while True:
            try:
                choice = self.input_or_cancel("\nEnter task ID (or 'b' to go back): ")
            
            except OperationCancelled:
                print("\nℹ️  Operation cancelled. Returning to main menu.")
                return None
        
            if choice not in valid_ids:
                print("\n❗ Invalid ID. Please enter a number from the list.")
            else:
                return int(choice)

    # Function that interacts with the user to update task status
    def update_task(self):
        try:
            task_id = self.select_task_id()

            if task_id is None:
                return

            while True:
                try:
                    new_status = self.input_or_cancel(
                        "\nEnter new status ('done' or 'in progress', or 'b' to go back): "
                    )
                    new_status = normalize_state(new_status)

                    if new_status in ['done', 'in progress']:
                        break
                    else:
                        print("\n❗ Invalid status. Please enter only 'in progress' or 'done'.")
               
                except OperationCancelled:
                    print("\nℹ️ Operation cancelled. Returning to main menu.")
                    return
                
            if self.db.update_task_db(task_id, new_status):
                print("\n✅ Task status was updated.")

        except Exception as error:
            print(f"\n❌ Something went wrong: {error}")

    # Function for interactive task deletion through user input
    def delete_task(self):
        try:
            task_id = self.select_task_id()
            if task_id is None:
                return

            try:
                confirmation = self.input_or_cancel(f"\nAre you sure you want to delete the task with ID {task_id}? (y/n, or 'b' to cancel): ").lower()
                if confirmation == "y":
                    if self.db.delete_task_db(task_id):
                        print("\n🗑️ Task was successfully deleted.")
                else:
                    print("\nℹ️ Deletion cancelled.")
            
            except OperationCancelled:
                print("\nℹ️ Operation cancelled. Returning to main menu.")
        
        except Exception as error:
            print(f"❌ Error while deleting task: {error}")
    
    def input_or_cancel(self, prompt):
        user_input = input(prompt).strip()
        if user_input.lower() in ("b", "back"):
            raise OperationCancelled()
        return user_input


class OperationCancelled(Exception):
    """Exception to indicate user cancelled the operation."""
    pass
