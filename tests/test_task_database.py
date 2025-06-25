# test_task_manager
import pytest
from tests.test_init import create_test_db, create_test_table, drop_test_db, drop_test_table
from src.db_config import connect_to_test_db
from src.task_database import TaskDatabase
import mysql.connector
from mysql.connector import Error


# Fixture to create and drop test database and table for the entire test session
@pytest.fixture(scope="session", autouse=True)
def db_connection():
    create_test_db()
    connection = connect_to_test_db()
    yield connection
    connection.close()
    drop_test_db()


# Fixture for each test function to work with the cursor
@pytest.fixture(scope="function", autouse=True)
def db_cursor(db_connection):
    create_test_table()
    cursor = db_connection.cursor()
    yield cursor
    cursor.close()
    drop_test_table()


"""TESTS"""


# Test: verifies that a valid task is correctly inserted into the database
def test_add_task_db_valid(db_connection, db_cursor):
    title = "Test Task"
    description = "Description of test task"

    task_db = TaskDatabase(db_connection) # create an instance with connection
    task_db.add_task_db(title, description) # call the instance method

    db_cursor.execute("SELECT title, description FROM tasks ORDER BY id DESC LIMIT 1")
    result = db_cursor.fetchone()

    assert result == (title, description)


# Test: verifies that inserting a task with NULL title fails at the database level
def test_add_task_db_rejects_null(db_connection, db_cursor):
    title = None
    description = "Test description"

    task_db = TaskDatabase(db_connection)  # create instance

    db_cursor.execute("SELECT COUNT(*) FROM tasks")
    count_before = db_cursor.fetchone()[0]

    with pytest.raises(mysql.connector.Error):
        task_db.add_task_db(title, description)  # call method on instance
    
    db_cursor.execute("SELECT COUNT(*) FROM tasks")
    count_after = db_cursor.fetchone()[0]

    assert count_before == count_after


# Test: verifies that the database rejects a task with an empty title (even though Python validation happens before)
@pytest.mark.parametrize("invalid_title", ["", "   "])
def test_add_task_db_rejects_empty_title(db_connection, db_cursor, invalid_title):
    description = "Test description"

    task_db = TaskDatabase(db_connection)
    # Get count of tasks before attempt
    db_cursor.execute("SELECT COUNT(*) FROM tasks")
    count_before = db_cursor.fetchone()[0]
    
    # Expect a database error due to empty title values
    with pytest.raises(mysql.connector.Error):
        task_db.add_task_db(invalid_title, description)

    # Get count of tasks after attempt
    db_cursor.execute("SELECT COUNT(*) FROM tasks")
    count_after = db_cursor.fetchone()[0]

    # Verify the number of tasks has not changed
    assert count_before == count_after


# Tests that fetching a task returns a task correctly 
# if it has status "not started" or "in progress"
def test_fetch_task(db_connection, db_cursor):
    task_db = TaskDatabase(db_connection)

    # Insert tasks with different statuses
    tasks = [
        ("Task 1", "Description 1", "not started"),
        ("Task 2", "Description 1", "in progress"),
        ("Task 3", "Description 3", "done"), # This should not be fatched
    ]

    db_cursor.executemany(
        "INSERT INTO tasks (title, description, status) VALUES (%s, %s, %s)",
        tasks
    )
    db_connection.commit()

    # Fetch tasks
    fetched_tasks = task_db.fetch_tasks_db()

    # Check that only tasks with allowed statuses are returned
    fetched_titles = []
    for task in fetched_tasks:
        fetched_titles.append(task[1])
    
    assert "Task 1" in fetched_titles
    assert "Task 2" in fetched_titles
    assert "Task 3" not in fetched_titles


def test_select_task_id_db_returns_ids_and_titles(db_connection, db_cursor):
    task_db = TaskDatabase(db_connection)

    # Insert test data
    tasks = [
        ("Task A", "Description A"),
        ("Task B", "Description B"),
    ]
    db_cursor.executemany("INSERT INTO tasks (title, description) VALUES (%s, %s)", tasks)
    db_connection.commit()

    # Fetch using method
    result = task_db.select_task_id_db()

    # There should be two results, matching what we inserted
    fetched_titles = [title for _, title in result]
    
    assert "Task A" in fetched_titles
    assert "Task B" in fetched_titles

    # Check that IDs are integers
    for task_id, title in result:
        assert isinstance(task_id, int)
        assert isinstance(title, str)


# Test: verifies that updating task status to valid values ('in progress' / 'done') works correctly
@pytest.mark.parametrize("new_status", ["in progress", "done"])
def test_update_status_db_valid_input(db_connection, db_cursor, new_status):
    title = "Test task for update"
    description = "Task description"
    initial_status = "not started"

    task_db = TaskDatabase(db_connection)

    # Directly insert test task into database
    db_cursor.execute(
        "INSERT INTO tasks (title, description, status) VALUES (%s, %s, %s)",
        (title, description, initial_status)
    )
    db_connection.commit()

    # Get ID of newly inserted task
    db_cursor.execute("SELECT id FROM tasks ORDER BY id DESC LIMIT 1")
    task_id = db_cursor.fetchone()[0]

    # Perform the update
    update_ok = task_db.update_task_db(task_id, new_status)
    assert update_ok is True

    # Verify the change in database
    db_cursor.execute("SELECT status FROM tasks WHERE id = %s", (task_id,))
    status_in_db = db_cursor.fetchone()[0]
    assert status_in_db == new_status


# Test: verifies that attempting to update task status to an invalid value returns False
def test_update_status_db_invalid_status(db_connection, db_cursor):
    task_db = TaskDatabase(db_connection)

    # First insert a task to test on
    db_cursor.execute(
        "INSERT INTO tasks (title, description) VALUES (%s, %s)",
        ("Task for invalid status test", "Description")
    )
    db_connection.commit()

    db_cursor.execute("SELECT id FROM tasks ORDER BY id DESC LIMIT 1")
    task_id = db_cursor.fetchone()[0]

    # Get original status of the task (default)
    db_cursor.execute("SELECT status FROM tasks WHERE id = %s", (task_id,))
    status_before = db_cursor.fetchone()[0]

    # Try updating to an invalid status
    invalid_status = "Waiting for confirmation"

    update_ok = task_db.update_task_db(task_id, invalid_status)
    assert update_ok is False

    # Verify status did not change
    db_cursor.execute("SELECT status FROM tasks WHERE id = %s", (task_id,))
    status_after = db_cursor.fetchone()[0]
    assert status_before == status_after


# Test: verifies deleting a task from the database
def test_delete_task_db_valid_task(db_connection, db_cursor):
    title = "Task to delete"
    description = "Description of deletable task"
    
    task_db = TaskDatabase(db_connection)

    db_cursor.execute(
        "INSERT INTO tasks (title, description) VALUES (%s, %s)", (title, description)
    )
    db_connection.commit()

    db_cursor.execute("SELECT id FROM tasks ORDER BY id DESC LIMIT 1")
    task_id = db_cursor.fetchone()[0]

    # Verify that deletion attempt succeeds
    delete_ok = task_db.delete_task_db(task_id)
    assert delete_ok is True

    # Verify task was deleted
    db_cursor.execute("SELECT COUNT(*) FROM tasks WHERE id = %s", (task_id,))
    count = db_cursor.fetchone()[0]
    assert count == 0


# Test: verifies that attempting to delete a task with invalid ID returns False
def test_delete_task_db_invalid_id(db_connection, db_cursor):
    invalid_id = 999999  # Assume this ID does not exist in DB

    task_db = TaskDatabase(db_connection)

    db_cursor.execute("SELECT COUNT(*) FROM tasks")
    count_before = db_cursor.fetchone()[0]

    # Try deleting task with invalid ID, expect False
    delete_ok = task_db.delete_task_db(invalid_id)
    assert delete_ok is False

    db_cursor.execute("SELECT COUNT(*) FROM tasks")
    count_after = db_cursor.fetchone()[0]

    # Verify the number of tasks has not changed (no task was deleted)
    assert count_before == count_after


# pytest tests/test_task_database.py -s
