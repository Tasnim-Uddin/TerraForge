import base64
import os
import string

from flask import Flask, request, jsonify
import hashlib
import secrets
import sqlite3

from werkzeug.utils import secure_filename

DATABASE_NAME = "user_database.db"

SERVER_IP = "10.192.41.216"


class Server:
    def __init__(self):

        self.app = Flask(__name__)
        self.app.config["PLAYER_SAVE_FOLDER"] = "player_save_files"
        self.app.config["WORLD_SAVE_FOLDER"] = "world_save_files"

        if not os.path.exists(path=self.app.config["PLAYER_SAVE_FOLDER"]):
            os.makedirs(name=self.app.config["PLAYER_SAVE_FOLDER"])
        if not os.path.exists(path=self.app.config["WORLD_SAVE_FOLDER"]):
            os.makedirs(name=self.app.config["WORLD_SAVE_FOLDER"])

        # Define routes
        self.app.add_url_rule(rule="/register", endpoint="register_user", view_func=self.register_user,
                              methods=["POST"])
        self.app.add_url_rule(rule="/authenticate", endpoint="authenticate_user", view_func=self.authenticate_user,
                              methods=["POST"])
        self.app.add_url_rule(rule="/authenticate_recovery_code", endpoint="authenticate_recovery_code", view_func=self.authenticate_recovery_code,
                              methods=["POST"])
        self.app.add_url_rule(rule="/reset_password", endpoint="reset_password",
                              view_func=self.reset_password,
                              methods=["POST"])
        self.app.add_url_rule(rule="/upload", endpoint="upload_files", view_func=self.upload_files,
                              methods=["POST"])
        self.app.add_url_rule(rule="/download", endpoint="download_files", view_func=self.download_files,
                              methods=["GET"])

    def run(self):
        self.create_tables()
        self.app.run(host=SERVER_IP, port=5000)

    @staticmethod
    def create_tables():
        connection = sqlite3.connect(DATABASE_NAME)
        cursor = connection.cursor()
        # Create the users table with ID and username as primary key
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (      
                                        USER_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                        username TEXT UNIQUE NOT NULL,
                                        hashed_password TEXT NOT NULL,
                                        password_salt TEXT NOT NULL,
                                        hashed_recovery_code TEXT NOT NULL,
                                        recovery_code_salt TEXT NOT NULL
                                    )""")

        # Create the save_files table with username as foreign key
        cursor.execute("""CREATE TABLE IF NOT EXISTS save_files (      
                                    SAVE_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                    username TEXT NOT NULL,
                                    file_path TEXT NOT NULL,
                                    file_type TEXT NOT NULL,
                                    UNIQUE(username, file_path, file_type),
                                    FOREIGN KEY (username) REFERENCES users(username)
                                )""")
        connection.commit()
        connection.close()

    @staticmethod
    def register_user():
        data = request.json
        username = data.get("username")
        password = data.get("password")

        print("Received registration request for username:", username)

        # Generate salt and hash the password
        password_salt = secrets.token_hex(16)
        salted_password = password + password_salt
        hashed_password = hashlib.sha256(salted_password.encode()).hexdigest()

        # Generate password_salt and hash the recovery code
        recovery_code_length = 6
        recovery_code = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(recovery_code_length))
        recovery_code_salt = secrets.token_hex(16)
        salted_recovery_code = recovery_code + recovery_code_salt
        hashed_recovery_code = hashlib.sha256(salted_recovery_code.encode()).hexdigest()

        try:
            # Insert user data into the database
            with sqlite3.connect(database=DATABASE_NAME) as connection:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO users (username, hashed_password, password_salt, hashed_recovery_code, recovery_code_salt) VALUES (?, ?, ?, ?, ?)",
                               (username, hashed_password, password_salt, hashed_recovery_code, recovery_code_salt))
                connection.commit()
            print("User registered successfully:", username)
            return jsonify({"success": True, "recovery code": recovery_code})
        except sqlite3.IntegrityError:
            # Return error if username already exists
            print("Registration failed. Username already exists:", username)
            return jsonify({"error": "Registration failed. Username already exists."})

    @staticmethod
    def authenticate_user():
        data = request.json
        username = data.get("username")
        password = data.get("password")

        print("Received authentication request for username:", username)

        try:
            # Retrieve user data from the database
            with sqlite3.connect(database=DATABASE_NAME) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT hashed_password, password_salt FROM users WHERE username=?", (username,))
                user = cursor.fetchone()

                if user:
                    stored_hashed_password, stored_password_salt = user
                    # Hash the input password with the stored salt
                    hashed_password_with_salt = hashlib.sha256((password + stored_password_salt).encode()).hexdigest()

                    # Check if the hashed input password with stored salt matches the stored hashed password with salt
                    if hashed_password_with_salt == stored_hashed_password:
                        print("User authenticated successfully:", username)
                        return jsonify({"authenticated": True})

                print("Authentication failed. Invalid username or password:", username)
                return jsonify({"authenticated": False, "error": "Invalid username or password."})
        except Exception as error:
            print("Error during authentication:", str(error))
            return jsonify({"error": str(error)})

    @staticmethod
    def authenticate_recovery_code():
        data = request.json
        username = data.get("username")
        recovery_code = data.get("recovery code")

        print("Received recovery code authentication request for username:", username, "and code:", recovery_code)

        try:
            # Retrieve user data from the database
            with sqlite3.connect(database=DATABASE_NAME) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT hashed_recovery_code, recovery_code_salt FROM users WHERE username=?", (username,))
                user = cursor.fetchone()

                if user:
                    stored_hashed_recovery_code, stored_recovery_code_salt = user
                    # Hash the input recovery code with the stored salt
                    hashed_recovery_code_with_salt = hashlib.sha256((recovery_code + stored_recovery_code_salt).encode()).hexdigest()

                    # Check if the hashed input recovery code with stored salt matches the stored hashed recovery code with salt
                    if hashed_recovery_code_with_salt == stored_hashed_recovery_code:
                        print("User recovery code authenticated successfully:", username)
                        return jsonify({"authenticated": True})

                print("Authentication failed. Invalid username or recovery code:", username)
                return jsonify({"authenticated": False, "error": "Invalid username or recovery code."})
        except Exception as error:
            print("Error during authentication:", str(error))
            return jsonify({"error": str(error)})

    @staticmethod
    def reset_password():
        data = request.json
        username = data.get("username")
        password = data.get("password")

        print("Received new password request for username:", username)

        # Generate salt and hash the password
        password_salt = secrets.token_hex(16)
        salted_password = password + password_salt
        hashed_password = hashlib.sha256(salted_password.encode()).hexdigest()

        # Generate password_salt and hash the recovery code
        recovery_code_length = 6
        recovery_code = ''.join(
            secrets.choice(string.ascii_letters + string.digits) for _ in range(recovery_code_length))
        recovery_code_salt = secrets.token_hex(16)
        salted_recovery_code = recovery_code + recovery_code_salt
        hashed_recovery_code = hashlib.sha256(salted_recovery_code.encode()).hexdigest()

        try:
            # Insert user data into the database
            with sqlite3.connect(database=DATABASE_NAME) as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "UPDATE users SET hashed_password = ?, password_salt = ?, hashed_recovery_code = ?, recovery_code_salt = ? WHERE username = ?",
                    (hashed_password, password_salt, hashed_recovery_code, recovery_code_salt, username))
                connection.commit()
            print("New password set successfully:", username)
            return jsonify({"success": True, "recovery code": recovery_code})
        except Exception as error:
            print("Error when setting new password:", str(error))
            return jsonify({"error": str(error)})

    # Client requesting to upload a file to server
    def upload_files(self):
        username = request.form.get("username")
        player_file = request.files["player"]
        world_file = request.files["world"]

        if player_file and world_file:
            player_filename = secure_filename(player_file.filename)
            world_filename = secure_filename(world_file.filename)
            player_file_path = os.path.join(self.app.config["PLAYER_SAVE_FOLDER"], player_filename)
            world_file_path = os.path.join(self.app.config["WORLD_SAVE_FOLDER"], world_filename)

            player_file.save(player_file_path)
            world_file.save(world_file_path)

            print("Files uploaded by user:", username)

            with sqlite3.connect(database=DATABASE_NAME) as connection:
                cursor = connection.cursor()
                try:
                    cursor.execute("INSERT INTO save_files (username, file_path, file_type) VALUES (?, ? ,?)",
                                   (username, player_filename, "player"))
                except Exception as error:
                    print("player insert error:", error)
                try:
                    cursor.execute("INSERT INTO save_files (username, file_path, file_type) VALUES (?, ? ,?)",
                                   (username, world_filename, "world"))
                except Exception as error:
                    print("world insert error:", error)
                connection.commit()
            return jsonify({"success": True})
        else:
            return jsonify({"error": "No file uploaded"})

    # Client requesting to download a file from server
    def download_files(self):
        username = request.args.get("username")
        try:
            with sqlite3.connect(database=DATABASE_NAME) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT file_path, file_type FROM save_files WHERE username=?", (username,))
                paths = cursor.fetchall()

                if paths:
                    files_to_send = []

                    for record in paths:
                        filename = record[0]
                        filetype = record[1]
                        print(filename, filetype)
                        if filetype == "player":
                            file_path = os.path.join(self.app.config["PLAYER_SAVE_FOLDER"], filename)
                        elif filetype == "world":
                            file_path = os.path.join(self.app.config["WORLD_SAVE_FOLDER"], filename)
                        with open(file_path, "rb") as file:
                            file_content = file.read()
                        files_to_send.append(((filetype, filename), file_content))

                    file_data = []
                    for file_info, file_content in files_to_send:
                        file_content_encoded = base64.b64encode(file_content).decode(
                            "utf-8")  # Encode bytes to base64 string so that no problems parsing
                        file_data.append((file_info, file_content_encoded))

                    return jsonify({"files": file_data})

                else:
                    return jsonify({"error": "No files found for the user"})

        except Exception as error:
            return jsonify({"error": str(error)})


if __name__ == "__main__":
    server = Server()
    server.run()
