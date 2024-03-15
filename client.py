import base64
import os

import requests
from global_constants import PLAYER_SAVE_FOLDER, WORLD_SAVE_FOLDER

SERVER_URL = "http://192.168.0.80:5000"


class Client:
    def __init__(self, game):
        self.__username = game.get_username()

    def register_user(self, password):
        print("Sending registration request for username:", self.__username)

        """Send plaintext username and password to the server. 
        All hashing and salting done server side Should be using HTTPS to prevent MITM attacks, 
        but I am not due to lack of digital certificate/self-signed certificates"""

        data = {"username": self.__username, "password": password}
        url = SERVER_URL + "/register"
        response = requests.post(url, json=data)

        print("Response:", response.text)
        return response.json()

    def authenticate_user(self, password):
        print("Sending authentication request for username:", self.__username)

        # Send plaintext username and password to the server
        data = {"username": self.__username, "password": password}
        url = SERVER_URL + "/authenticate"
        response = requests.post(url, json=data)

        print("Response:", response.text)
        user_data = response.json()

        if "authenticated" in user_data and user_data["authenticated"]:
            print("User authenticated successfully:", self.__username)
            return True
        else:
            print("Authentication failed:", user_data.get("error", "Unknown error"))
            return False

    def upload_files(self, player_file_path, world_file_path):
        print("Uploading files for username:", self.__username)
        url = SERVER_URL + "/upload"
        player_file = open(os.path.join(PLAYER_SAVE_FOLDER, f"{player_file_path}.json"), "rb")
        world_file = open(os.path.join(WORLD_SAVE_FOLDER, f"{world_file_path}.json"), "rb")
        files = {"player": player_file, "world": world_file}
        username = {"username": self.__username}
        response = requests.post(url, files=files, data=username)
        if response.status_code == 200:
            print("File uploaded successfully:", player_file)
            print("File uploaded successfully:", world_file)
        else:
            print("Failed to upload files:", response.text)

    def download_files(self):
        if not os.path.exists(path=PLAYER_SAVE_FOLDER):
            os.makedirs(name=PLAYER_SAVE_FOLDER)
        if not os.path.exists(path=WORLD_SAVE_FOLDER):
            os.makedirs(name=WORLD_SAVE_FOLDER)

        print("Downloading files for username:", self.__username)
        url = SERVER_URL + "/download"
        response = requests.get(url, params={"username": self.__username})

        if response.status_code == 200:
            files_data = response.json().get("files", [])
            for file_info, file_content_encoded in files_data:
                file_type = file_info[0]
                file_name = file_info[1]
                file_content = base64.b64decode(file_content_encoded)
                if file_type == "player":
                    with open(file_name, "wb") as file:
                        file.write(file_content)
                elif file_type == "world":
                    with open(file_name, "wb") as file:
                        file.write(file_content)
                print("File downloaded successfully:", file_name)
        else:
            print("Failed to download files:", response.text)
