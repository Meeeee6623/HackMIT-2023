import json

import weaviate


class VectorDB:
    def __init__(self, weaviate_url, weaviate_key="key"):
        try:
            if weaviate_key is None:
                self.db = weaviate.Client(
                    url=weaviate_url,
                )
            else:
                self.db = weaviate.Client(
                    url=weaviate_url,
                    auth_client_secret=weaviate.AuthApiKey(api_key=weaviate_key),
                )
            print("Weaviate client successfully created.")
        except Exception as e:
            print("Failed to create Weaviate client. Error: ", e)

            # check if yt classes exist
        # VectorDB("http://44.209.9.231:8080", youtube_key=os.environ["YOUTUBE_API_KEY"])
        # Create an instance of VectorDB

        if not self.db.schema.exists("Playlist"):
            try:
                with open("/classes/playlist.json", "r") as f:
                    print("Playlist class file opened successfully.")
            except Exception as e:
                print("Failed to open playlist class file. Error: ", e)
                playlist = json.load(f)
                print(
                    "Loaded playlist JSON: ",
                    json.dumps(playlist, indent=4)[:100],
                    "...",
                )  # print first 100 characters of the JSON for debugging
            self.db.schema.create_class(playlist)
        if not self.db.schema.exists("video"):
            with open("/classes/video.json", "r") as f:
                video = json.load(f)
                print(
                    "Loaded video JSON: ", json.dumps(video, indent=4)[:100], "..."
                )  # print first 100 characters of the JSON for debugging
            self.db.schema.create_class(video)
        if not self.db.schema.exists("topic"):
            with open("/classes/topic.json", "r") as f:
                topic = json.load(f)
                print(
                    "Loaded topic JSON: ", json.dumps(topic, indent=4)[:100], "..."
                )  # print first 100 characters of the JSON for debugging
            self.db.schema.create_class(topic)

    def print_existing_classes(self):
        try:
            classes = self.db.schema.get()
            print("Classes: ", classes)
            print("Existing classes in the Weaviate schema:")
            for cls in classes:
                if isinstance(cls, str):
                    print(f"cls is a string: {cls}")
                else:
                    print("cls is not a dict")
        except Exception as e:
            print("Failed to fetch existing classes. Error: ", e)

    def check_playlist(self, query, certainty):
        # self.print_existing_classes()

        near_text = {
            "concepts": [query],
            "certainty": certainty,
        }
        results = (
            self.db.query.get(class_name="Playlist", properties=["playlistID"])
            .with_near_text(near_text)
            .with_additional("id")
            .do()["data"]["Get"]["Playlist"]
        )
        if len(results) > 0:
            return results[0]
        else:
            return False

    def add_videos(self, video_list, playlist_id):
        """
        Adds videos from the playlist to the database
        :param video_list: list of video information to add, with params title, description, id
        :param playlist_id: id of the playlist that the videos are from
        :return:
        """

        # batch add videos to db
        with self.db.batch(
            batch_size=20,
            num_workers=4,
            dynamic=True,
        ) as batch:
            for video in video_list:
                batch.add_data_object(
                    data_object={
                        "title": video["title"],
                        "description": video["description"],
                        "playlistID": playlist_id,
                        "videoID": video["id"],
                    },
                    class_name="Video",
                )

    def add_topics(self, topics, videoID):
        """
        Adds topics from the video to the database
        :param topics: list of topics to add, with fields: topic, startTime
        :param videoID: ID of the video that the topics are from
        :return:
        """

        # batch add topics to db
        with self.db.batch(
            batch_size=20,
            num_workers=4,
            dynamic=True,
        ) as batch:
            for topic in topics:
                batch.add_data_object(
                    data_object={
                        "topic": topic["topic"],
                        "text": topic["text"],
                        "startTime": topic["startTime"],
                        "videoID": videoID,
                    },
                    class_name="Topic",
                )
        pass

    def add_playlist(self, playlist_id, title, description):
        """
        Adds playlist to the database
        :param playlist_id: ID of the playlist
        :param title: title of the playlist
        :param description: playlist description
        :return:
        """

        self.db.data_object.create(
            data_object={
                "title": title,
                "description": description,
                "playlistID": playlist_id,
            },
            class_name="Playlist",
        )

    def search_videos(self, playlistID, user_query):
        """
        Searches for videos in a playlist
        :param playlistID: the ID of the playlist to search in
        :param user_query: the query to search for
        :return:
        """
        near_text = {
            "concepts": [user_query],
        }
        where_filter = {
            "path": ["playlistID"],
            "operator": "Equal",
            "valueString": playlistID,
        }

        query = self.db.query.get(
            "Video",
            ["videoID"],
        )
        print(f"Query: {query.build()}")

        results = (
            query.with_where(where_filter)
            .with_near_text(near_text)
            .do()["data"]["Get"]["Video"]
        )
        print(results)
        # rest of your code...
        if len(results) > 0:
            return results[0]
        else:
            return False

    def search_topics(self, videoID, user_query):
        """
        Searches for topics in a video
        :param videoID: ID of the video to search in
        :param user_query: query to search for
        :return:
        """
        near_text = {
            "concepts": [user_query],
        }
        where_filter = {
            "path": ["videoID"],
            "operator": "Equal",
            "valueString": videoID,
        }
        results = (
            self.db.query.get("Topic", ["topic", "startTime"])
            .with_where(where_filter)
            .with_near_text(near_text)
            .do()["data"]["Get"]["topic"]
        )
        if len(results) > 0:
            return results[0]
        else:
            return False
