import re

def is_valid_email(email: str) -> bool:
    if not isinstance(email, str):
        return False
    pattern = r"^[\w\.-]+@[\w\.-]+\.(fr|com)$"
    return re.match(pattern, email) is not None

def is_valid_phone(phone: str) -> bool:
    if not isinstance(phone, str):
        return False
    phone = phone.strip().replace(" ", "")
    return phone.isdigit() and 9 <= len(phone) <= 10