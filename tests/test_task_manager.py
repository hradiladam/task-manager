# test_task_manager
import pytest
from unittest.mock import MagicMock
from src.task_manager import TaskManager, OperationCancelled

# Test that add_task() sends the correct data to the db through add_task_db function
def test_add_task_valid_input(monkeypatch):
    mock_db = MagicMock()

    # Simulate user input
    inputs = iter(["Test Title", "Test Description"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    
    manager = TaskManager(mock_db)
    manager.add_task()
    mock_db.add_task_db.assert_called_once_with("Test Title", "Test Description")


# Test that add_task() handles exceptions from the DB and prints an error message
def test_add_task_db_exception(monkeypatch, capsys):
    mock_db = MagicMock()
    # Make add_task_db raise an exception when called
    mock_db.add_task_db.side_effect = Exception("DB connection error")

    inputs = iter(["Valid Title", "Valid Description"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    manager = TaskManager(mock_db)
    manager.add_task()

    # Capture printed output
    captured = capsys.readouterr()

    # Assert error and the exceptions details was printed 
    assert "Something went wrong:" in captured.out
    assert "DB connection error" in captured.out


# Test that add_task() rejects invalid inputs (empty or whitespace-only)
# and only calls add_task_db once valid input is provided
def test_add_task_rejects_invalid_inputs_until_valid(monkeypatch):
    mock_db = MagicMock()

    inputs = iter([
        "", "Valid Description",             # 1st: empty title
        "Valid Title", "",                   # 2nd: empty description
        "   ", "Valid Description",          # 3rd: whitespace-only title
        "Valid Title", "   ",                # 4th: whitespace-only description
        "Valid Title", "Valid Description"   # 5th: valid input
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    manager = TaskManager(mock_db)
    manager.add_task()
    mock_db.add_task_db.assert_called_once_with("Valid Title", "Valid Description")


# Test that select_task_id() informs when the task list is empty
def test_select_task_id_empty_list(capsys):
    mock_db = MagicMock()
    mock_db.fetch_task_ids_db.return_value = []

    manager = TaskManager(mock_db)
    result = manager.select_task_id()

    captured = capsys.readouterr()
    assert result is None
    assert "The task list is empty" in captured.out


# tes tthat show_tasks() informs when the task list is empty   
def test_show_tasks_empty_list(capsys):
    mock_db = MagicMock()
    mock_db.fetch_tasks_db.return_value = []

    manager = TaskManager(mock_db)
    result = manager.show_tasks()

    captured = capsys.readouterr()
    assert result is None
    assert "No tasks to display." in captured.out


# Test that update_task() correctly updates a task's statu swhen given valid user inputs
# including input that would accepted for normalization
@pytest.mark.parametrize("user_inputs, expected_call", [
    (["1", "done"], (1, "done")),
    (["2", "in progress"], (2, "in progress")), 
    (["3", "inprogress"], (3, "in progress")), # testing no space (normalized)    
])
def test_update_task_various_valid_inputs(monkeypatch, user_inputs, expected_call):
    mock_db = MagicMock()
    mock_db.fetch_task_ids_db.return_value = [(1, "Task A"), (2, "Task B"), (3, "Task C")]
    mock_db.update_task_db.return_value = True

    inputs = iter(user_inputs)
    monkeypatch.setattr("builtins.input", lambda _: next(inputs)) 

    manager = TaskManager(mock_db)
    manager.update_task()

    mock_db.update_task_db.assert_called_once_with(*expected_call)


# Test that update_task() retries if the user first enters an invalid ID
# and only proceeds once a valid task ID and status are provided
def test_update_task_rejects_invalid_inputs_until_valid(monkeypatch):
    mock_db = MagicMock()
    mock_db.fetch_task_ids_db.return_value = [(1, "Task A"), (2, "Task B")]
    mock_db.update_task_db.return_value = True

    inputs = iter(["999", "2", "done" ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    manager = TaskManager(mock_db)
    manager.update_task()

    mock_db.update_task_db.assert_called_once_with(2, "done")


# Test that update_task() does NOT call update_task_db
# if the user enters only invalid statuses and the input runs out.
def test_update_task_all_invalid_status(monkeypatch):
    mock_db = MagicMock()
    mock_db.fetch_task_ids_db.return_value = [(1, "Task A")]

    # User selects valid ID "1", then enters 5 invalid statuses
    inputs = iter(["1", "started", "waiting", "pending", "123", ""])  # all invalid
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    manager = TaskManager(mock_db)
    manager.update_task()

    # Should never reach the DB update
    mock_db.update_task_db.assert_not_called()


# Test that update_task() handles DB exceptions and prints an error message
def test_update_task_db_exception(monkeypatch, capsys):
    mock_db = MagicMock()
    mock_db.fetch_task_ids_db.return_value = [(1, "Task A")]
    mock_db.update_task_db.side_effect = Exception("DB update failure")

    inputs = iter(["1", "done"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    manager = TaskManager(mock_db)
    manager.update_task()

    captured = capsys.readouterr()
    assert "Something went wrong" in captured.out
    assert "DB update failure" in captured.out


# Test that delete_task() calls the db if valid input provided
# Test that delete_task() calls the db if valid input is provided
def test_delete_task_valid_input(monkeypatch):
    mock_db = MagicMock()
    mock_db.fetch_task_ids_db.return_value = [(1, "Task A")]
    mock_db.delete_task_db.return_value = True  # Simulate successful deletion

    # First input is task ID, second is confirmation "y"
    inputs = iter(["1", "y"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    manager = TaskManager(mock_db)
    manager.delete_task()

    # Assert that delete_task_db was called with the correct task ID
    mock_db.delete_task_db.assert_called_once_with(1)
    

# Test that delete_task() handles exceptions from the DB and prints an error message
def test_delete_task_db_exception(monkeypatch, capsys):
    mock_db = MagicMock()
    mock_db.fetch_task_ids_db.return_value = [(1, "Task A")]
    mock_db.delete_task_db.side_effect = Exception ("DB delete failure")

    inputs = iter(["1", "y"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    manager = TaskManager(mock_db)
    manager.delete_task()

    captured = capsys.readouterr()
    assert "Error while deleting task" in captured.out
    assert "DB delete failure" in captured.out
    

# Test that delete_task() does not call delete_task_db when user cancels
def test_delete_task_rejects_invalid_ids_until_valid_then_cancel(monkeypatch):
    mock_db = MagicMock()
    # Provide a valid task list with IDs 1 and 2
    mock_db.fetch_task_ids_db.return_value = [(1, "Task A"), (2, "Task B")]

    # Simulate invalid IDs first ("999", "abc"), then valid ID "2",
    # then user cancels deletion by inputting "n"
    inputs = iter(["999", "abc", "2", "n"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    manager = TaskManager(mock_db)
    manager.delete_task()

    # Should NOT call delete_task_db because user canceled
    mock_db.delete_task_db.assert_not_called()


def test_input_or_cancel(monkeypatch):
    manager = TaskManager(None)  # db argument is not needed here

    # Test that normal input returns the input string
    monkeypatch.setattr("builtins.input", lambda _: "normal input")
    assert manager.input_or_cancel("Prompt: ") == "normal input"

    # Test that 'b' raises OperationCancelled
    monkeypatch.setattr("builtins.input", lambda _: "b")
    with pytest.raises(OperationCancelled):
        manager.input_or_cancel("Prompt: ")

    # Test that 'back' (case insensitive) raises OperationCancelled
    monkeypatch.setattr("builtins.input", lambda _: "Back")
    with pytest.raises(OperationCancelled):
        manager.input_or_cancel("Prompt: ")

# pytest tests/test_task_manager.py




