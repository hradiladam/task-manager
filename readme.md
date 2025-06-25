# Task Manager

A simple command-line task manager written in Python that uses MySQL to store tasks.  
You can add, view, update, and delete tasks directly from your terminal.


---

## Features

- Add tasks with title and description  
- View tasks (only those not done yet)  
- Update task status ('done' or 'in progress')  
- Delete tasks by ID  
- Cancel operation and return to main manu by typing `b` or `back`  
- Uses MySQL to store tasks  
- Automated tests included with pytest

### What is tested?

- Database operations (`tests/test_task_database.py`):
- Task Manager logic (`tests/test_task_manager.py`):

### How tests work
- Tests use a dedicated MySQL test database (`test_task_manager`).  
- The `test_init.py` script creates the testing database and necessary tables before tests run, and cleans up afterward.  
- Pytest fixtures handle setup and teardown of database connections and cursors.  
- Tests for `TaskManager` mock database methods and simulate user input.  

---

## Setup & Installation

### Requirements

- Python 3.9 or higher  
- MySQL server installed and running locally  
- Basic knowledge of command line / terminal  

### Steps

1. **Clone the repository:**
```bash
git clone https://github.com/your-username/task-manager.git
cd task-manager
```

2. **Create and activate a virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure database password**
- Create a .env file in the project root with the following content (replace your_mysql_password with your actual MySQL password): DB_PASSWORD=your_mysql_password

5. **Setup the MySQL database**
- You can manually create the database named task_manager in your MySQL server, or
- Run the program once to let it create the tasks table automatically.

### Run the program
```bash
python src/main.py
```

### Structure

task-manager/
-- src/
    -- main.py
    -- db_config.py
    -- task_database.py
    -- task_manager.py
    -- utils.py

-- tests/
    -- test_task_database.py
    -- test_task_manager.py
    --test_init.py

-- .venv/
-- .env
-- requirements.txt
-- README.md
-- pytest.ini
