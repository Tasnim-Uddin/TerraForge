import requests

SERVER_URL = "http://192.168.0.40:5000"


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

