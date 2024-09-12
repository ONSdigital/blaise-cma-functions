import re


def extract_username_from_case_id(string):
    """
    Extracts a username from a given string based on a specific pattern.

    The pattern used for extraction is:
    - Optionally starts with a digit(s) followed by a hyphen (e.g., '1-', '424-')
    - Followed by one or more word characters (letters, digits, and underscores)

    Returns:
    - Whole username (if no digits are at the front, e.g., 'bob',)
    - All characters after the first dash (if digits are at the front, e.g., '34-bob')

    """

    match = re.match(r"^(\d+)-(.+)$", string)
    if match:
        return match.group(2)
    else:
        return string
