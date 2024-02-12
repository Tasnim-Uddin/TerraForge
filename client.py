import base64
import os

import requests
from global_constants import *

SERVER_URL = "http://192.168.0.80:5000"


class Client:
    def register_user(self, username, password):
        print("Sending registration request for username:", username)

        """Send plaintext username and password to the server. 
        All hashing and salting done server side Should be using HTTPS to prevent MITM attacks, 
        but I am not due to lack of digital certificate/self-signed certificates"""

        data = {"username": username, "password": password}
        url = SERVER_URL + "/register"
        response = requests.post(url, json=data)

        print("Response:", response.text)
        return response.json()

    def authenticate_user(self, username, password):
        print("Sending authentication request for username:", username)

        # Send plaintext username and password to the server
        data = {"username": username, "password": password}
        url = SERVER_URL + "/authenticate"
        response = requests.post(url, json=data)

        print("Response:", response.text)
        user_data = response.json()

        if "authenticated" in user_data and user_data["authenticated"]:
            print("User authenticated successfully:", username)
            return True
        else:
            print("Authentication failed:", user_data.get("error", "Unknown error"))
            return False

    def upload_file(self, username, file_path, file_type):
        print("Uploading file:", file_path)
        url = SERVER_URL + "/upload"
        if file_type == "player":
            files = {'file': open(os.path.join(PLAYER_SAVE_FOLDER, f"{file_path}.json"), 'rb')}
        elif file_type == "world":
            files = {'file': open(os.path.join(WORLD_SAVE_FOLDER, f"{file_path}.json"), 'rb')}
        data = {"username": username, "file_type": file_type}
        response = requests.post(url, files=files, data=data)
        print("Response:", response.text)

    def download_files(self, username):
        if not os.path.exists(path=PLAYER_SAVE_FOLDER):
            os.makedirs(name=PLAYER_SAVE_FOLDER)
        if not os.path.exists(path=WORLD_SAVE_FOLDER):
            os.makedirs(name=WORLD_SAVE_FOLDER)

        print("Downloading files for username:", username)
        url = SERVER_URL + "/download"
        response = requests.get(url, params={"username": username})

        if response.status_code == 200:
            files_data = response.json().get("files", [])
            print(files_data)
            for file_info, file_content_encoded in files_data:
                file_type = file_info[0]
                file_name = file_info[1]
                print(file_type)
                file_content = base64.b64decode(file_content_encoded)
                if file_type == "player":
                    with open(file_name, 'wb') as file:
                        file.write(file_content)
                elif file_type == "world":
                    with open(file_name, 'wb') as file:
                        file.write(file_content)
                print("File downloaded successfully:", file_name)
        else:
            print("Failed to download files:", response.text)
