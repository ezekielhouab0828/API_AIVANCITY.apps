
import hashlib
from utils.db import fetch_one, execute_query

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username: str, password: str):
    user = fetch_one("SELECT * FROM users WHERE username = %s", (username,))
    if not user:
        return None

    hashed = hash_password(password)
    if hashed == user["password_hash"]:
        return user
    return None

def create_user(username: str, password: str, role: str = "user"):
    hashed = hash_password(password)
    execute_query(
        "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
        (username, hashed, role)
    )