from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi


class YoutubeConnector:
    def __init__(self, api_key):
        self.yt = build('youtube', 'v3', developerKey=api_key)

    def search_playlists(self, query, num_playlists=5):
        # get playlist IDs, title, description, and thumbnail
        response = self.yt.search().list(part="snippet", q=query, type="playlist", maxResults=num_playlists).execute()
        playlists = []

        for item in response['items']:
            playlists.append({
                'id': item['id']['playlistId'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'thumbnail': item['snippet']['thumbnails']['default']['url']
            })
        return playlists

    def get_videos(self, playlist_id):
        """
        Get all video titles, descriptions, IDs from a playlist
        :param playlist_id: playlist to get videos from
        :return:
        """
        response = self.yt.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50
        ).execute()
        videos = []
        for item in response['items']:
            videos.append({
                'id': item['snippet']['resourceId']['videoId'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description']
            })
        return videos

    def get_transcript(self, videoID):
        """
        Get the transcript of a video
        :param videoID: ID of the video to get the transcript of
        :return:
        """
        transcript = YouTubeTranscriptApi.get_transcript(videoID)
        return transcript


