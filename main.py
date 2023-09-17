import modal
from modal import Image, Mount, Stub, asgi_app, gpu, method
from pathlib import Path
from pydantic import BaseModel

import os
import re



image = modal.Image.debian_slim().pip_install(
    "youtube_transcript_api", "weaviate-client", "google-api-python-client"
)

stub = modal.Stub("yt-search")


@stub.function(
    image=image,
    mounts=[
        modal.Mount.from_local_dir(
            "classes",
            remote_path="/classes",
        ),
        modal.Mount.from_local_python_packages("WeaviateLink"),
        modal.Mount.from_local_python_packages("YouTubeLink"),
        modal.Mount.from_local_python_packages("OpenAILink"),


        modal.Mount.from_local_dir(
            "frontend",
            remote_path="/root/frontend",
        ),
    ],
)
@asgi_app()
def app():
    frontend_path = Path(__file__).parent / "frontend"

    import fastapi.staticfiles
    from fastapi import FastAPI

    from WeaviateLink import VectorDB
    from OpenAILink import OpenAI_Connector
    from YouTubeLink import YoutubeConnector

    db = VectorDB("http://44.209.9.231:8080")
    openai = OpenAI_Connector(os.environ["OPENAI_API_KEY"])
    yt = YoutubeConnector(os.environ["YOUTUBE_API_KEY"])



    conversation = []


    web_app = FastAPI()


    @web_app.post("/ask/{query}")
    async def ask(query: str):
        # Initialize the variables
        yt_query = ""
        tone = ""

    
        # Get the response from the chatbot
        response, conversation = openai.get_yt_search(query, conversation)

        # Check for yt query in [] brackets
        regex = r"\[(.*?)\]"
        matches = re.findall(regex, response)
        if len(matches) > 0:
            continue_chat = False
            yt_query = matches[0]

        # Check for tone behavior in ** brackets
        regex = r"\*\*(.*?)\*\*"
        matches = re.findall(regex, response)
        if len(matches) > 0:
            tone = matches[0]

        return {"reply": response, "yt_query": yt_query, "tone": tone}



    @web_app.get("/train/{playlist}")
    async def train_chatbot(playlist: str):
        # Logic from yt-chain.py goes here
        # For example:
        playlistID = db.check_playlist(playlist, certainty=0.8)["playlistID"]
        if not playlistID:
            # search yt
            yt_search = openai.get_yt_search(playlist)
            playlist_list = yt.search_playlists(yt_search)
            # ... and so on
        return {"message": f"Training started with {playlist}"}

    @web_app.get("/chat/{query}")
    async def chat(query: str):
        # Logic from yt-chain.py goes here
        # For example:
        videoID = db.search_videos(playlistID, query)['videoID']
        topic = db.search_topics(videoID, query)
            # Select the first playlist from the search results
            selected_playlist = playlist_list[0]
            # Get the playlist ID
            playlistID = selected_playlist['id']
            # Save the playlist to the database
            db.save_playlist(playlistID, selected_playlist)
        return {"reply": reply}

    @web_app.get("/infer/{prompt}")
    async def infer(prompt: str):
        return {f"message": "{prompt}"}

    web_app.mount(
        "/", fastapi.staticfiles.StaticFiles(directory=str(frontend_path), html=True)
    )
    return web_app


def get_info(query, conversation):
    

def setup():
    db = VectorDB("http://44.209.9.231:8080")
    openai = OpenAI_Connector(os.environ["OPENAI_API_KEY"])
    yt = YoutubeConnector(os.environ["YOUTUBE_API_KEY"])

