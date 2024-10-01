import sqlite3
import hashlib
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

    @staticmethod
    def get_user_by_id(user_id):
        conn = sqlite3.connect("blogs_advanced.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(row[0], row[1], row[2])
        return None

    @staticmethod
    def get_user_by_username(username):
        conn = sqlite3.connect("blogs_advanced.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, password, role FROM users WHERE username = ?",
            (username,),
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return row
        return None

    @staticmethod
    def verify_password(stored_password, provided_password):
        # Hash the provided password and compare with the stored hash
        return stored_password == hashlib.sha256(provided_password.encode()).hexdigest()
