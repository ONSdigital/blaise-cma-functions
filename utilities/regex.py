import re

def extract_username(string):
    pattern = r"(?:\d-)?(\w+)(?:-\d)?" 
    match = re.search(pattern, string)

    if match:
        return match.group(1)
    else:
        return None 