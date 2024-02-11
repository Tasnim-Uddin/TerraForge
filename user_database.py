import sqlite3
import hashlib
import secrets


class UserDatabase:
    def __init__(self, database_name="user_database.db"):
        self.connection = sqlite3.connect(database=database_name)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users (      
                                    username TEXT PRIMARY KEY NOT NULL,
                                    password TEXT NOT NULL,
                                    salt TEXT NOT NULL
                                )""")
        self.connection.commit()

    def register_user(self, username, password):
        # Generate a random salt to make hashed password more secure against rainbow tables
        salt = secrets.token_hex(16)
        # Combine the password and salt
        salted_password = password + salt
        # Hash the salted password
        hashed_password = hashlib.sha256(string=salted_password.encode()).hexdigest()
        try:
            self.cursor.execute("INSERT INTO users (username, password, salt) VALUES (?, ?, ?)",
                                (username, hashed_password, salt))
            self.connection.commit()
            print("Registration successful.")
            return True
        except sqlite3.IntegrityError:
            print("Registration failed. Username already exists.")
            return False

    def authenticate_user(self, username, password):
        # Retrieve the salt associated with the username
        self.cursor.execute("SELECT salt FROM users WHERE username=?", (username,))
        salt = self.cursor.fetchone()
        if salt:
            # Combine the provided password with the retrieved salt
            salted_password = password + salt[0]
            # Hash the salted password
            hashed_password = hashlib.sha256(string=salted_password.encode()).hexdigest()
            # Check if the username and hashed password match
            self.cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_password))
            user = self.cursor.fetchone()
            if user:
                print("Login successful.")
                return True
        print("Login failed. Invalid username or password.")
        return False

    def close_connection(self):
        self.connection.close()
