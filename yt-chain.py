import os

from WeaviateLink import VectorDB
from OpenAILink import OpenAI_Connector
from YouTubeLink import YoutubeConnector

db = VectorDB("http://44.209.9.231:8080")
openai = OpenAI_Connector(os.environ["OPENAI_API_KEY"])
yt = YoutubeConnector(os.environ["YOUTUBE_API_KEY"])

# input from user
user_query = input("Welcome to Athena. What would you like to learn about today?")
# check if information already in DB
playlistID = db.check_playlist(user_query, certainty=0.8)['playlistID'] # might need gpt call to modify text/search?
if not playlistID:
    # search yt
    yt_search = openai.get_yt_search(user_query) # text search string
    playlist_list = yt.search_playlists(yt_search) # format: list of dicts with keys: id, title, description, thumbnail

    # get playlist ID - ask user for confirmation
    # WILL be replaced with GUI
    print("Here are some playlists I found:")
    for playlist in playlist_list:
        print(f"Title: {playlist['title']}, ID: {playlist['id']}")
    playlist_id = input("Which playlist would you like to learn from? (Enter ID)")
    # get correct playlist object
    playlist = [playlist for playlist in playlist_list if playlist['id'] == playlist_id][0]

    # get playlist description and add to database
    description = openai.get_playlist_search(playlist['title'], playlist['description'])
    db.add_playlist(playlist_id, playlist['title'], description)

    # get video IDs for the playlist
    video_list = yt.get_videos(playlist_id)

    # describe videos and add them to the playlist
    for video in video_list:
        video['description'] = openai.get_video_description(video['title'], video['description'])
    # upload videos to weaviate
    db.add_videos(video_list, playlist_id)


    # chunk each video into topics
    for video in video_list:
        transcript = yt.get_transcript(video['id']) # transcript has keys: text, start, duration
        video['topics'] = openai.get_video_topics(transcript)
        # add to DB
        db.add_topics(video['topics'], video['id'])
    pass

# search within playlist
videoID = db.search_videos(playlistID, user_query)['videoID']

# search within video
topic = db.search_topics(videoID, user_query)

# return video results + chunk and return text

