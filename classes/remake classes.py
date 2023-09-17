import json

import weaviate


db = weaviate.Client("http://44.209.9.231:8080")

db.schema.delete_class("Playlist")
db.schema.delete_class("Video")
db.schema.delete_class("Topic")

print("Classes deleted.")

print("Creating classes...")

with open("classes/playlist.json", "r") as f:
    playlist = json.load(f)
    db.schema.create_class(playlist)

with open("classes/video.json", "r") as f:
    video = json.load(f)
    db.schema.create_class(video)

with open("classes/topic.json", "r") as f:
    topic = json.load(f)
    db.schema.create_class(topic)