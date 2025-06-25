# test_utils
import pytest
from src.utils import validate_task, normalize_state


# Tests that chacks that normalize state returnes modified
@pytest.mark.parametrize("input_status, expected", [
    ("in progress", "in progress"),
    ("InProgress", "in progress"),
    ("In progres", "in progress"),
    ("inprogres", "in progress"),
    ("inproggres", "in progress"),
    ("inproggress", "in progress"),
    ("inprogess", "in progress"),
    ("inprogesss", "in progress"),
    ("inprogrees", "in progress"),
    ("inprgress", "in progress"),
    ("inprogresss", "in progress"),
    ("inprogressss", "in progress"),
    ("in  progress", "in progress"),
    (" in   progress ", "in progress"),
    (" in progress ", "in progress"),
])
def test_normalize_state(input_status, expected):
    assert normalize_state(input_status) == expected


# Tests that chacks that returned value from validate_task ic correcct
@pytest.mark.parametrize("title, description, expected", [
    ("", "desc", "Task title and description must not be empty or contain only spaces."),
    ("title", "", "Task title and description must not be empty or contain only spaces."),
    ("   ", "desc", "Task title and description must not be empty or contain only spaces."),
    ("title", "   ", "Task title and description must not be empty or contain only spaces."),
    ("title", "desc", None),
])
def test_validate_task(title, description, expected):
    assert validate_task(title.strip(), description.strip()) == expected

# pytest tests/test_utils.py -s