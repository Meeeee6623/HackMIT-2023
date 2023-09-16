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

large_chunk_schema = {
    "class": "YT_large",
    "properties": [
        {
            "name": "transcriptChunk",
            "dataType": ["text"],
            "description": "The transcript chunk of the video",
            "moduleConfig": {
                "text2vec-openai": {
                    "skip": False,
                    "vectorizePropertyName": False,
                }
            }
        },
        {
            "name": "videoID",
            "dataType": ["text"],
            "description": "The ID of the video",
            "moduleConfig": {
                "text2vec-openai": {
                    "skip": True,
                    "vectorizePropertyName": False,
                }
            }
        },
        {
            "name": "startTime",
            "dataType": ["number"],
            "description": "The start time of the chunk in the video",
            "moduleConfig": {
                "text2vec-openai": {
                    "skip": True,
                }
            }
        },
        {
            "name": "duration",
            "dataType": ["number"],
            "description": "The duration of the chunk in the video",
            "moduleConfig": {
                "text2vec-openai": {
                    "skip": True,
                }
            }
        },
        {
            "name": "playlistID",
            "dataType": ["text"],
            "description": "The ID of the playlist that the video is in",
            "moduleConfig": {
                "text2vec-openai": {
                    "skip": True,
                }
            }
        }
    ]
}

small_chunk_schema = {
    "class": "YT_small",
    "properties": [
        {
            "name": "transcriptChunk",
            "dataType": ["text"],
            "description": "The transcript chunk of the video",
            "moduleConfig": {
                "text2vec-openai": {
                    "skip": False,
                    "vectorizePropertyName": False,
                }
            }
        },
        {
            "name": "timestamp",
            "dataType": ["number"],
            "description": "The timestamp of the text in the video",
            "moduleConfig": {
                "text2vec-openai": {
                    "skip": True,
                    "vectorizePropertyName": False,
                }
            }
        },
        {
            "name": "parentChunk",
            "dataType": ["text"],
            "description": "The ID of the (large) parent chunk in weaviate",
            "moduleConfig": {
                "text2vec-openai": {
                    "skip": True,
                    "vectorizePropertyName": False,
                }
            }
        }
    ]
}

# dump to file
with open("YT_large.json", "w") as f:
    json.dump(large_chunk_schema, f, indent=2)

with open("YT_small.json", "w") as f:
    json.dump(small_chunk_schema, f, indent=2)

with open("default_class.json", "w") as f:
    json.dump(default_schema, f, indent=2)


