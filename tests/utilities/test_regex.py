from utilities.regex import extract_username_from_case_id


def test_with_digit_and_hyphen():
    assert extract_username_from_case_id("123-username") == "username"


def test_with_multiple_digits_and_hyphen():
    assert extract_username_from_case_id("45678-johndoe") == "johndoe"


def test_with_no_digits_or_hyphen():
    assert extract_username_from_case_id("username") == "username"


def test_with_no_digits_but_with_hyphen():
    assert extract_username_from_case_id("abc-xyz") == "abc-xyz"


def test_empty_string():
    assert extract_username_from_case_id("") == ""


def test_only_digits():
    assert extract_username_from_case_id("12345") == "12345"


def test_no_match_with_special_characters():
    assert extract_username_from_case_id("1234_username") == "1234_username"
