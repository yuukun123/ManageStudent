import re

def is_valid_email(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,4}$", email) is not None

def is_valid_phone(phone):
    return re.match(r"^0\d{9}$", phone) is not None

def is_valid_null(value):
    return value is not None

def is_valid_name(name):
    return re.match(r"^[a-zA-Z\s]+$", name) is not None

