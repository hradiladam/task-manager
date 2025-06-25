# utils

# Function to normalize mistyped state values for "in progress"
def normalize_state(status):
    status = status.strip().lower()
    # Remove all spaces for matching
    compressed = status.replace(" ", "")

    accepted_variants = {
        "inprogress",
        "in progres",
        "inprogres",
        "inproggres",
        "inproggress",
        "inprogres",
        "inproggress",
        "inprogess",
        "inprogesss",
        "inprogres",
        "inprogrees",
        "inprgress",
        "inprgress",
        "inprogresss",
        "inprogressss"
    }

    if compressed in accepted_variants:
        return "in progress"
    return status


# Validate task title and description.
# Returns error message string if invalid, otherwise None.
def validate_task(title: str, description: str) -> str | None:
        if not title:
            return "Task title and description must not be empty or contain only spaces."
        if not description:
            return "Task title and description must not be empty or contain only spaces."
        return None