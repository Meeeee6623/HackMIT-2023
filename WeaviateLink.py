import json

import openai
import weaviate

from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi


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
        # check if yt classes exist
        if not self.db.schema.exists("YT_large"):
            with open("YT_large.json", "r") as f:
                YT_large = json.load(f)
            self.db.schema.create_class(YT_large)
        if not self.db.schema.exists("YT_small"):
            with open("YT_small.json", "r") as f:
                YT_small = json.load(f)
            self.create_class(YT_small)

    def create_class(self, class_name):
        if self.db.schema.exists(class_name):
            print(f"{class_name} already exists")
        else:
            with open("default_class.json", "r") as f:
                new_class = json.load(f)
            new_class["class"] = class_name
            self.db.schema.create_class(class_name)

    def add_playlist(self, playlistID, chunk_length=300, yt_api_key=None):
        """
        Adds a playlist to the database in large chunks
        :param playlistID: id of the playlist to add
        :param chunk_length: length of each chunk in characters
        :param yt_api_key: YouTube api key
        :return:
        """
        # check if playlist already in db
        where_filter = {
            "path": ["playlistID"],
            "operator": "Equal",
            "valueText": f"{playlistID}",
        }
        playlist = self.db.query.get("YT_large", ["playlistID"]).with_where(where_filter).do()["data"]["Get"][
            "YT_large"]
        if len(playlist) > 0:
            # playlist already in db
            print(f"playlist {playlistID} already in db, skipping")
            return
        print(f"uploading playlist: {playlistID}")
        # get video IDs
        youtube = build("youtube", "v3", developerKey=yt_api_key)
        response = youtube.playlistItems().list(part="contentDetails", playlistId=playlistID, maxResults=50).execute()
        video_ids = []

        for t in response['items']:
            print(t['contentDetails']['videoId'])
            video_ids.append(t['contentDetails']['videoId'])

        # get transcripts

        for videoID in video_ids:
            # check if video already in db
            where_filter = {
                "path": ["videoID"],
                "operator": "Equal",
                "valueText": f"{videoID}",
            }
            video = self.db.query.get("YT_large", ["videoID"]).with_where(where_filter).do()["data"]["Get"]["YT_large"]
            if len(video) > 0:
                # video already in db
                print(f"video {videoID} already in db, skipping")
                continue
            transcript = YouTubeTranscriptApi.get_transcript(videoID, languages=['en'])
            # chunk into chunk_length size chunks
            large_chunks = []
            chunk = ""
            duration = 0
            for i, t in enumerate(transcript):
                if len(chunk) + len(t['text']) > chunk_length:
                    large_chunks.append({"text": chunk, "start": float(t['start']), "duration": float(duration)})
                    print(large_chunks[-1])
                    chunk = t['text']
                    duration = float(t['duration'])
                chunk += t['text']
                duration += float(t['duration'])

            # upload to weaviate
            # batch add chunks to db

            with self.db.batch(
                    batch_size=20,
                    num_workers=4,
                    dynamic=True,
            ) as batch:
                for i, chunk in enumerate(large_chunks):
                    batch.add_data_object(
                        data_object={
                            "transcriptChunk": chunk['text'],
                            "playlistID": playlistID,
                            "startTime": chunk['start'],
                            "videoID": videoID,
                            "duration": chunk['duration'],
                        },
                        class_name="YT_large",
                    )
            print(f"added {len(large_chunks)} large chunks")

    def add_small_chunks(self, videoID, parentID, startTime, duration):
        """
        Adds small chunks to the database for a given video
        Args:
            videoID: id of the video that the chunks are from
            parentID: id of the parent chunk associated with the small chunks
            startTime: where the parent chunk starts in the video
            duration: how long the parent chunk is
        """
        # get transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id=videoID, languages=['en'])
        # chunk into 2-wide chunks within the large chunk window
        small_chunks = []
        chunk = ""
        for i, t in enumerate(transcript):
            # append small chunks (2 transcript bits long)
            if t['start'] < startTime:
                pass
            elif t['start'] > startTime + duration:
                break
            if not i + 2 >= len(transcript):
                chunk = transcript[i]['text'] + transcript[i + 1]['text']
                small_chunks.append({"text": chunk, "start": float(t['start'])})
        # batch upload to weaviate
        with self.db.batch(
                batch_size=20,
                num_workers=4,
                dynamic=True,
        ) as batch:
            for small_chunk in small_chunks:
                batch.add_data_object(
                    data_object={
                        "transcriptChunk": small_chunk['text'],
                        "timestamp": small_chunk['start'],
                        "parentChunk": parentID,
                    },
                    class_name="YT_small",
                )

    def query_yt_coarse(self, query, playlistID=None):
        """
        Queries the large chunks of the YouTube database for a given query
        :param query: string to search for
        :param playlistID: (optional) playlist to search within
        :return: large chunk ID, certainty
        """
        if playlistID is not None:
            where_filter = {
                "path": ["playlistID"],
                "operator": "Equal",
                "valueText": f"{playlistID}",
            }
            large_chunks = (
                self.db.query.get("YT_large", ["transcriptChunk", 'videoID', 'startTime', 'duration'])
                .with_where(where_filter)
                .with_near_text({"concepts": [query]})
                .with_additional(["id", "certainty"])
                .do()["data"]["Get"]["YT_large"]
            )

        else:
            large_chunks = (
                self.db.query.get("YT_large", ["transcriptChunk", 'videoID', 'startTime', 'duration'])
                .with_near_text({"concepts": [query]})
                .with_additional(["id", "certainty"])
                .do()["data"]["Get"]["YT_large"]
            )

        if len(large_chunks) == 0:
            return None, None, None, None, None
        # get the best match
        return large_chunks[0]['_additional']['id'], large_chunks[0]['_additional']['certainty'], large_chunks[0][
            'videoID'], large_chunks[0]['startTime'], large_chunks[0]['duration']

    def query_yt_fine(self, query, parentID, videoID, startTime, duration, vectorStrength=0.5):
        """
        Queries the small chunks of the YouTube database for a given query
        :param query: text to search for
        :param chunkID: ID of large (parent) chunk
        :param vectorStrength: strength of vector search
                :return: videoID, timestamp
        """
        # check if small chunks exist
        where_filter = {
            "path": ["parentChunk"],
            "operator": "Equal",
            "valueText": f"{parentID}",
        }
        small_chunks = (self.db.query
        .get("YT_small", ["transcriptChunk", "timestamp"])
        .with_where(where_filter)
        .with_hybrid(query=query, properties=["transcriptChunk"], alpha=vectorStrength)
        .do()["data"]["Get"]["YT_small"])

        if not small_chunks:
            # no small chunks exist
            print(f"adding small chunks for {videoID}")
            self.add_small_chunks(videoID, parentID, startTime, duration)
            # search again
            small_chunks = (self.db.query
            .get("YT_small", ["transcriptChunk", "timestamp"])
            .with_where(where_filter)
            .with_hybrid(query=query, properties=["transcriptChunk"], alpha=vectorStrength)
            .do()["data"]["Get"]["YT_small"])
        # get video id
        video_id = videoID
        # get timestamp
        timestamp = small_chunks[0]["timestamp"]
        return video_id, timestamp

    def query_yt_full(self, query, playlistID=None):
        """
        Queries the YouTube database for a given query
        :param query: string to search for
        :param playlistID: (optional) playlist to search within
        :return: Best video match for the query (dict) with videoID, timestamp
        """
        # upload playlist if not already in db
        if playlistID is not None:
            self.add_playlist(playlistID)

        # coarse search
        chunkID, certainty = self.query_yt_coarse(query, playlistID)

        # fine search
        if chunkID is not None:
            return self.query_yt_fine(query, chunkID, certainty)

        # no match found
        return None, None

    def add_website(self, website_url):
        pass

    def query_website(self, query, website_url):
        pass
