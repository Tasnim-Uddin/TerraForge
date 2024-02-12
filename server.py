from flask import Flask, request, jsonify
import hashlib
import secrets
import sqlite3

DATABASE_NAME = "user_database.db"


class Server:
    def __init__(self):
        self.app = Flask(__name__)

        # Define routes
        self.app.add_url_rule(rule="/register", endpoint="register_user", view_func=self.register_user,
                              methods=["POST"])
        self.app.add_url_rule(rule="/authenticate", endpoint="authenticate_user", view_func=self.authenticate_user,
                              methods=["POST"])

    def create_tables(self):
        connection = sqlite3.connect(database=DATABASE_NAME)
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (      
                                username TEXT PRIMARY KEY NOT NULL,
                                hashed_password TEXT NOT NULL,
                                salt TEXT NOT NULL
                            )""")
        connection.commit()
        connection.close()

    def register_user(self):
        data = request.json
        username = data.get("username")
        password = data.get("password")

        print("Received registration request for username:", username)

        # Generate salt and hash the password
        salt = secrets.token_hex(16)
        salted_password = password + salt
        hashed_password = hashlib.sha256(salted_password.encode()).hexdigest()

        try:
            # Insert user data into the database
            with sqlite3.connect(database=DATABASE_NAME) as connection:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO users (username, hashed_password, salt) VALUES (?, ?, ?)",
                               (username, hashed_password, salt))
                connection.commit()
            print("User registered successfully:", username)
            return jsonify({"success": True})
        except sqlite3.IntegrityError:
            # Return error if username already exists
            print("Registration failed. Username already exists:", username)
            return jsonify({"error": "Registration failed. Username already exists."})

    def authenticate_user(self):
        data = request.json
        username = data.get("username")
        password = data.get("password")

        print("Received authentication request for username:", username)

        try:
            # Retrieve user data from the database
            with sqlite3.connect(database=DATABASE_NAME) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT hashed_password, salt FROM users WHERE username=?", (username,))
                user = cursor.fetchone()

                if user:
                    stored_hashed_password, stored_salt = user
                    # Hash the input password with the stored salt
                    hashed_password_with_salt = hashlib.sha256((password + stored_salt).encode()).hexdigest()

                    # Check if the hashed input password with stored salt matches the stored hashed password with salt
                    if hashed_password_with_salt == stored_hashed_password:
                        print("User authenticated successfully:", username)
                        return jsonify({"authenticated": True})

                print("Authentication failed. Invalid username or password:", username)
                return jsonify({"authenticated": False, "error": "Invalid username or password."})
        except Exception as error:
            print("Error during authentication:", str(error))
            return jsonify({"error": str(error)})

    def run(self):
        self.create_tables()
        self.app.run(host="192.168.0.40", port=5000)


if __name__ == "__main__":
    server = Server()
    server.run()
