import re


def extract_username_from_case_id(string):
    """
    Extracts a username from a given string based on a specific pattern.

    The pattern used for extraction is:
    - Optionally starts with a digit followed by a hyphen (e.g., '1-')
    - Followed by one or more word characters (letters, digits, and underscores)

    Args:
        string (str): The input string from which to extract the username.

    Returns:
        str: The extracted username if a match is found, otherwise None.
    """

    match = re.match(r'^(\d+)-(.+)$', string)
    if match:
        return match.group(2)
    else:
        return string