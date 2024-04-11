import base64
import os

import requests
import socket
from global_constants import PLAYER_SAVE_FOLDER, WORLD_SAVE_FOLDER


class Client:

    def __init__(self):
        self.server_ip = None
        self.server_url = None

    def set_server(self, server_ip):
        self.server_ip = server_ip
        self.server_url = f"http://{server_ip}:5000"

    def verify_server(self):
        try:
            # Attempt to connect to the server
            with socket.create_connection(address=(self.server_ip, 5000), timeout=5) as sock:
                # If connection successful, return True
                return True
        except socket.error:
            # If connection fails, return False
            return False

    def close_connection(self):
        # Send a request to the server indicating that the connection is closed
        data = {"message": "Closing connection"}
        url = self.server_url + "/close_connection"
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("Connection closed successfully.")
        else:
            print("Failed to close connection:", response.text)

    def register_user(self, username, password):
        print("Sending registration request for username:", username)

        """Send plaintext username and password to the server. 
        All hashing and salting done server side should be using HTTPS to prevent MITM attacks, 
        but I am not due to lack of digital certificate/self-signed certificates"""

        data = {"username": username, "password": password}
        url = self.server_url + "/register"
        response = requests.post(url, json=data)

        print("Response:", response.text)
        user_data = response.json()
        if "success" in user_data and user_data["success"]:
            return True, user_data["recovery code"]
        else:
            return False, None

    def authenticate_user(self, username, password):
        print("Sending authentication request for username:", username)

        # Send plaintext username and password to the server
        data = {"username": username, "password": password}
        url = self.server_url + "/authenticate"
        response = requests.post(url, json=data)

        user_data = response.json()

        if "authenticated" in user_data and user_data["authenticated"]:
            print("User authenticated successfully:", username)
            return True
        else:
            print("Authentication failed:", user_data.get("error", "Unknown error"))
            return False

    def authenticate_recovery_code(self, username, recovery_code):
        print("Sending recovery code authentication request for username:", username)

        # Send plaintext username and recovery code to the server
        print(username, recovery_code)
        data = {"username": username, "recovery code": recovery_code}
        url = self.server_url + "/authenticate_recovery_code"
        response = requests.post(url, json=data)

        user_data = response.json()

        if "authenticated" in user_data and user_data["authenticated"]:
            print("User authenticated successfully:", username)
            return True
        else:
            print("Authentication failed:", user_data.get("error", "Unknown error"))
            return False

    def reset_password(self, username, new_password):
        print("Sending recovery code authentication request for username:", username)

        # Send plaintext username and password to the server
        data = {"username": username, "password": new_password}
        url = self.server_url + "/reset_password"
        response = requests.post(url, json=data)

        user_data = response.json()
        print(user_data["success"], user_data["recovery code"])
        if "success" in user_data and user_data["success"]:
            print("New password set successfully:", username)
            return True, user_data["recovery code"]
        else:
            print("Setting new password failed:", user_data.get("error", "Unknown error"))
            return False, None

    def upload_files(self, username, player_file_path, world_file_path):
        print("Uploading files for username:", username)
        url = self.server_url + "/upload"

        player_file = open(os.path.join(PLAYER_SAVE_FOLDER, f"{player_file_path}.json"), "rb")
        world_file = open(os.path.join(WORLD_SAVE_FOLDER, f"{world_file_path}.json"), "rb")
        files = {"player": player_file, "world": world_file}
        username = {"username": username}
        response = requests.post(url, files=files, data=username)
        if response.status_code == 200:
            print("File uploaded successfully:", player_file)
            print("File uploaded successfully:", world_file)
        else:
            print("Failed to upload files:", response.text)

    def download_files(self, username):
        if not os.path.exists(path=PLAYER_SAVE_FOLDER):
            os.makedirs(name=PLAYER_SAVE_FOLDER)
        if not os.path.exists(path=WORLD_SAVE_FOLDER):
            os.makedirs(name=WORLD_SAVE_FOLDER)

        print("Downloading files for username:", username)
        url = self.server_url + "/download"
        response = requests.get(url, params={"username": username})

        if response.status_code == 200:
            files_data = response.json().get("files", [])
            for file_info, file_content_encoded in files_data:
                file_type = file_info[0]
                file_name = file_info[1]
                file_content = base64.b64decode(file_content_encoded)
                if file_type == "player":
                    file_path = os.path.join(PLAYER_SAVE_FOLDER, file_name)
                    with open(file_path, "wb") as file:
                        file.write(file_content)
                elif file_type == "world":
                    file_path = os.path.join(WORLD_SAVE_FOLDER, file_name)
                    with open(file_path, "wb") as file:
                        file.write(file_content)
                print("File downloaded successfully:", file_name)
        else:
            print("Failed to download files:", response.text)
