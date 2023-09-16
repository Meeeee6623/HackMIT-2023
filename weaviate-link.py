import json

import openai
import weaviate

class VectorDB:
    def __init__(self, weaviate_url, weaviate_key, openai_key):
        self.db = weaviate.Client(
            url=weaviate_url,
            auth_client_secret=weaviate.AuthApiKey(
                api_key=weaviate_key
            ),
            additional_headers={"X-OpenAI-Api-Key": openai_key},
        )
        openai.api_key = openai_key

    def create_class(self, class_name):
        with open("default_class.json", "r") as f:
            new_class = json.load(f)
        new_class["class"] = class_name
        if self.db.schema.exists(class_name):
            print(f"{class_name} already exists")
        else:
            self.db.schema.create_class(class_name)


    def add_playlist(self, playlistID):
        pass


    def add_website(self, website_url):
        pass


    def query_yt(self, query, playlistID=None):
        pass


    def query_website(self, query, website_url):
        pass


