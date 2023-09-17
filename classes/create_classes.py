import json

default_schema = {
    "class": "Default_Chunk",
    "properties": [
        {
            "dataType": ["text"],
            "description": "Chunks of Text"
        }
    ]
}

playlist_schema = {
    "class": "Playlist",
    "properties": [
        {
            "name": "title",
            "dataType": ["text"],
            "description": "the title of the playlist",
            "moduleConfig": {
                "text2vec-openai": {
                    "skip": False,
                }
            }
        },
        {
            "name": "description",
            "dataType": ["text"],
            "description": "a description of the topics covered by the playlist",
            "moduleConfig": {
                "text2vec-openai": {
                    "skip": False,
                }
            }
        },
        {
            "name": "playlistID",
            "dataType": ["text"],
            "description": "the ID of the playlist",
            "moduleConfig": {
                "text2vec-openai": {
                    "skip": True,
                }
            }
        }
    ]
}

video_schema = {
    "class": "Video",
    "properties": [
        {
            "name": "title",
            "dataType": ["text"],
            "description": "the title of the video",
            "moduleConfig": {
                "text2vec-openai": {
                    "skip": False,
                }
            }
        },
        {
            "name": "description",
            "dataType": ["text"],
            "description": "a description of the topics covered by the video",
            "moduleConfig": {
                "text2vec-openai": {
                    "skip": False,
                }
            }
        },
        {
            "name": "playlistID",
            "dataType": ["text"],
            "description": "the ID of the playlist that the video is in",
            "moduleConfig": {
                "text2vec-openai": {
                    "skip": True,
                }
            }
        },
        {
            "name": "videoID",
            "dataType": ["text"],
            "description": "the ID of the video",
            "moduleConfig": {
                "text2vec-openai": {
                    "skip": True,
                }
            }
        },
    ]
}

topic_schema = {
    "class": "Topic",
    "properties": [
        {
            "name": "topic",
            "dataType": ["text"],
            "description": "the topic of the portion of the video",
        },
        {
            "name": "text",
            "dataType": ["text"],
            "description": "the text of the portion of the video relating to the topic",
        },
        {
            "name": "videoID",
            "dataType": ["text"],
            "description": "the ID of the video",
            "moduleConfig": {
                "text2vec-openai": {
                    "skip": True,
                }
            }
        },
        {
            "name": "startTime",
            "dataType": ["number"],
            "description": "the start time of the topic in the video",
            "moduleConfig": {
                "text2vec-openai": {
                    "skip": True,
                }
            }
        }

    ]
}


# dump to file
with open("playlist.json", "w") as f:
    json.dump(playlist_schema, f, indent=2)

with open("video.json", "w") as f:
    json.dump(video_schema, f, indent=2)

with open("topic.json", "w") as f:
    json.dump(topic_schema, f, indent=2)
