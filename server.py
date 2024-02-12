import base64
import os

from flask import Flask, request, jsonify
import hashlib
import secrets
import sqlite3

from werkzeug.utils import secure_filename

DATABASE_NAME = "user_database.db"
UPLOAD_FOLDER = "uploads"
PLAYER_SAVE_FOLDER = "player_save_files"
WORLD_SAVE_FOLDER = "world_save_files"

class Server:
    def __init__(self):
        if not os.path.exists(path=PLAYER_SAVE_FOLDER):
            os.makedirs(name=PLAYER_SAVE_FOLDER)
        if not os.path.exists(path=WORLD_SAVE_FOLDER):
            os.makedirs(name=WORLD_SAVE_FOLDER)

        self.app = Flask(__name__)
        self.app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        self.app.config['PLAYER_SAVE_FOLDER'] = PLAYER_SAVE_FOLDER
        self.app.config['WORLD_SAVE_FOLDER'] = WORLD_SAVE_FOLDER

        # Define routes
        self.app.add_url_rule(rule="/register", endpoint="register_user", view_func=self.register_user,
                              methods=["POST"])
        self.app.add_url_rule(rule="/authenticate", endpoint="authenticate_user", view_func=self.authenticate_user,
                              methods=["POST"])
        self.app.add_url_rule(rule="/upload", endpoint="upload_file", view_func=self.upload_file,
                              methods=["POST"])
        self.app.add_url_rule(rule="/download", endpoint="download_file", view_func=self.download_files,
                              methods=["GET"])

    def run(self):
        self.create_tables()
        self.app.run(host="192.168.0.80", port=5000)

    def create_tables(self):
        connection = sqlite3.connect(DATABASE_NAME)
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (      
                                username TEXT PRIMARY KEY NOT NULL,
                                hashed_password TEXT NOT NULL,
                                salt TEXT NOT NULL
                            )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS save_files (      
                                username TEXT PRIMARY KEY NOT NULL,
                                player_path TEXT,
                                world_path TEXT,
                                FOREIGN KEY (username) REFERENCES users(username)
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

    # Client requesting to upload a file to server
    def upload_file(self):
        username = request.form.get("username")
        file_type = request.form.get("file_type")  # Added to get the chosen file_type from the client
        file = request.files['file']
        if file:
            if file_type == 'player':
                folder_path = self.app.config['PLAYER_SAVE_FOLDER']
            elif file_type == 'world':
                folder_path = self.app.config['WORLD_SAVE_FOLDER']
            else:
                return jsonify({"error": "Invalid file_type specified"})

            filename = secure_filename(file.filename)
            file_path = os.path.join(folder_path, filename)
            file.save(file_path)
            print("File uploaded by user:", username)

            # Insert into save_files table
            with sqlite3.connect(database=DATABASE_NAME) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM save_files WHERE username = ?", (username,))
                row_count = cursor.fetchone()[0]

                if row_count == 0:
                    # Insert a new row if no row exists for the specified username
                    cursor.execute("INSERT INTO save_files (username, {}) VALUES (?, ?)".format(f"{file_type}_path"),
                                   (username, filename))
                else:
                    if file_type == "player":
                        # Update the existing row if a row exists for the specified username
                        cursor.execute(f"UPDATE save_files SET player_path = ? WHERE username = ?",
                                       (filename, username))
                    elif file_type == "world":
                        # Update the existing row if a row exists for the specified username
                        cursor.execute(f"UPDATE save_files SET world_path = ? WHERE username = ?",
                                       (filename, username))
                connection.commit()
            return jsonify({"success": True})
        else:
            return jsonify({"error": "No file uploaded"})

    # Client requesting to download a file from server
    def download_files(self):
        username = request.args.get("username")

        try:
            # Retrieve player_path and world_path associated with the username
            with sqlite3.connect(database=DATABASE_NAME) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT player_path, world_path FROM save_files WHERE username=?", (username,))
                paths = cursor.fetchone()

                if paths:
                    player_path, world_path = paths
                    files_to_send = []

                    # Add player file to files_to_send list
                    if player_path:
                        player_file_path = os.path.join(self.app.config['PLAYER_SAVE_FOLDER'], player_path)
                        with open(player_file_path, 'rb') as f:
                            player_content = f.read()
                        files_to_send.append((("player", player_file_path), player_content))

                    # Add world file to files_to_send list
                    if world_path:
                        world_file_path = os.path.join(self.app.config['WORLD_SAVE_FOLDER'], world_path)
                        with open(world_file_path, 'rb') as f:
                            world_content = f.read()
                        files_to_send.append((("world", world_file_path), world_content))

                    # Send files to the client
                    file_data = []
                    for file_name, file_content in files_to_send:
                        file_content_encoded = base64.b64encode(file_content).decode(
                            'utf-8')  # Encode bytes to base64 string so that no problems parsing
                        file_data.append((file_name, file_content_encoded))

                    return jsonify({"files": file_data})

                else:
                    return jsonify({"error": "No files found for the user"})

        except Exception as e:
            return jsonify({"error": str(e)})


if __name__ == "__main__":
    server = Server()
    server.run()
