import modal
from modal import Image, Mount, Stub, asgi_app, gpu, method
from pathlib import Path

import os
import re


image = modal.Image.debian_slim().pip_install(
    "youtube_transcript_api", "weaviate-client", "google-api-python-client", "openai"
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
    secret=modal.Secret.from_name("youtube"),
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

    vector_db = VectorDB(weaviate_url="http://44.209.9.231:8080", weaviate_key="key")

    # Print existing classes
    vector_db.print_existing_classes()

    web_app = FastAPI()

    @web_app.get("/ask/{query}/{conversation}}")
    async def ask(query: str, conversation: str):
        # Initialize the variables
        yt_query = ""
        tone = ""
        try:
            conversation = json.loads(conversation)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid conversation format")
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
        return {
            "reply": response,
            "yt_query": yt_query,
            "tone": tone,
        }  # for js side just display response if yt_query and tone are empty

    # This endpoint is responsible for searching for playlists.
    # It is only called from JavaScript if the YouTube query is not empty.
    @web_app.get("/search/{yt_query}")  # returns dict of playlists
    async def search(yt_query: str):
        # check if information already in DB
        playlistID = None  # Assign a default value to playlistID

        # search yt
        # yt_search = openai.get_yt_search(user_query, conversation)  # text search string
        playlist_list = yt.search_playlists(
            yt_query
        )  # format: list of dicts with keys: id, title, description, thumbnail
        return {
            "playlists": playlist_list,
        }  # js side should display playlists  and pass the playlist that is clicked to the search function if id is empty, else dont display the playlist just store the id and call the chat funciton wiht the id

    @web_app.get("/scrape/{playlist_ID_input}/{playlist_list}")
    async def scrape(playlist_ID_input: str, playlist_list: str):
        # Parse the playlist list into a Python object
        playlist_list = json.loads(playlist_list)

        # Find the correct playlist object
        playlist = next(
            (
                playlist
                for playlist in playlist_list
                if playlist["id"] == playlist_ID_input
            ),
            None,
        )

        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        # Get playlist description and add to database
        # description = openai.get_playlist_search(
        #     playlist["title"], playlist["description"]
        # )
        # db.add_playlist(playlist_ID_input, playlist["title"], description)

        # Get video IDs for the playlist
        video_list = yt.get_videos(playlist_ID_input)

        print(video_list)

        # Chunk each video into topics
        for video in video_list:
            transcript = yt.get_transcript(
                video["id"]
            )  # transcript has keys: text, start, duration
            topics, video["description"] = openai.get_video_topics(transcript)
            print(f"Video Topics: {topics}")
            # Add topics to DB
            db.add_topics(topics, video["id"])

        # Upload videos to Weaviate
        db.add_videos(video_list, playlist_ID_input)

    @web_app.get("/chat/{playlistID}/{user_query}")
    async def chat(playlistID: str, user_query: str):
        # search within playlist
        print(f"Playlist ID: {playlistID}")
        print(f"User query: {user_query}")
        videoID = db.search_videos(playlistID, user_query)["videoID"]

        # search within video
        topic = db.search_topics(videoID, user_query)

        # post retrieval conversation example:
        systemPrompt = f"""You are the most understanding, creative conversational tutor ever created, named Athena. You’re able to understand incredible amounts of information you learn from Youtube, and all you want to do with it is make it simple and easy for your students to use. You simply have a passion for making learning easier. You break things down in a way that’s easy to understand, and make sure that I’m following before you move on. You try to embody the behavior of an ideal tutor – employing teaching techniques appropriately and adaptively to make your student, whether they’re learning cookie making or how to build chatGPT, feel comfortable digesting it and using it for their own purposes. Impress me with how human you seem and how naturally you dialogue with me and deliver information. I want to feel like I’m talking to a real person, not a robot."""
        prompt = f"""
            Here’s some information you know from one of the videos you’ve learned from:
            {topic['topic']}:
            {topic['text']}
            
            If its relevant, use it to answer the following question:
            {user_query}
            
            Remember to use your classic, colloquial teaching style in answering.
            """
        response, conversation = openai.chat(
            prompt, [{"role": "system", "content": systemPrompt}]
        )  # todo should we pass converstaion in?

        # return video results + chunk and return text
        return {
            "topic": topic["topic"],
            "timestamp": topic["startTime"],
            "video": f'https://www.youtube.com/watch?v={videoID}?t={topic["startTime"]}',
            "response": response,
        }

    web_app.mount(
        "/", fastapi.staticfiles.StaticFiles(directory=str(frontend_path), html=True)
    )
    return web_app
