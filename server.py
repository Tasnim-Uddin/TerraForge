import base64
import json
import os

from flask import Flask, request, jsonify
import hashlib
import secrets
import sqlite3

from werkzeug.utils import secure_filename

DATABASE_NAME = "user_database.db"

SERVER_IP = "192.168.0.80"


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
        self.app.add_url_rule(rule="/upload", endpoint="upload_files", view_func=self.upload_files,
                              methods=["POST"])
        self.app.add_url_rule(rule="/download", endpoint="download_files", view_func=self.download_files,
                              methods=["GET"])

    def run(self):
        self.create_tables()
        self.app.run(host="192.168.0.80", port=5000)

    @staticmethod
    def create_tables():
        connection = sqlite3.connect(DATABASE_NAME)
        cursor = connection.cursor()
        # Create the users table with ID and username as primary key
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (      
                                        USER_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                        username TEXT UNIQUE,
                                        hashed_password TEXT NOT NULL,
                                        salt TEXT NOT NULL
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
                        files_to_send.append(((filetype, file_path), file_content))

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
