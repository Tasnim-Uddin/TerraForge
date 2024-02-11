import sqlite3
import hashlib


class UserDatabase:
    def __init__(self, db_name="user_database.db"):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                    id INTEGER PRIMARY KEY,
                                    username TEXT UNIQUE NOT NULL,
                                    password TEXT NOT NULL
                                )''')
        self.connection.commit()

    def register_user(self, username, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        try:
            self.cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            print("Username already exists.")
            return False

    def authenticate_user(self, username, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        self.cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_password))
        user = self.cursor.fetchone()
        if user:
            return True
        else:
            print("Invalid username or password.")
            return False

    def close_connection(self):
        self.connection.close()
