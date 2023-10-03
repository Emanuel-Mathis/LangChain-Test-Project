import pyrebase
from dotenv import find_dotenv, load_dotenv
import os
import requests
import json

class FirebaseHandler:
    def __init__(
        self
    ):
        load_dotenv(find_dotenv())
        api_key = os.environ.get("FIREBASE_API_KEY")
        auth_domain = os.environ.get("FIREBASE_AUTH_DOMAIN")
        db_url = os.environ.get("FIREBASE_DB_URL")
        project_id = os.environ.get("FIREBASE_PROJECT_ID")
        storage_bucket = os.environ.get("FIREBASE_STORAGE_BUCKET")
        #service_account = os.environ.get("FIREBASE_SERVICE_ACCOUNT")

        if api_key is None:
            raise ValueError("FIREBASE_API_KEY not found in environment variables.")

        config = {
            "apiKey": api_key,
            "authDomain": auth_domain,
            "databaseURL": db_url,
            "projectId": project_id,
            "storageBucket": storage_bucket
        }

        self.firebase = pyrebase.initialize_app(config)
        self.storage = self.firebase.storage()

    def retrieve_from_url(self, url):
        response = requests.get(url)
        return response
    
    def retrieve_url_from_firebase_file_name(self, file_name):
        return self.storage.child(file_name).get_url(None)