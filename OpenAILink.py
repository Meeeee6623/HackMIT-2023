import openai


class OpenAI_Connector:
    def __init__(self, api_key):
        openai.api_key = api_key
        openai.api_base = "https://api.openai.com/v1"

    def get_yt_search(self, user_query, conversation):
        prompt = f"""You're going to talk to me and see what I'd like you to become a tutor of. You're a system called Athena, that can learn to become a tutor on any set of knowledge by going to find the best Youtube playlists on it, watching them, and using them to help me. Use this conversation to decide what I know about the topic I'm interested in, etc.. You're not going to teach me here, your job is to find out exactly the type of thing I want to learn.  Alternatively, if I say I know exactly what I want, just let me commence the search.
        When you think you know what the student wants you to learn about, you'll follow these instructions:
        You are going to translate student's tutoring intent into Youtube searches that will bring up the most helpful playlists for that topic. For example, if our conversation so far has discussed that I want to know how to budget and I'm a beginner you might respond with "[Budgeting 101]". You'll respond only with this format [ (insert the the youtube search here) ]. Once you sent the [] wrapped Youtube Search there's no going back, I won't even see that message, as the system will pick up that this conversation is over. Double check before you send this message that I agree with you about what you'll be learning.  You're also going to output in * *  the behavioral instructions for the AI taking notes on the video on behalf of the student, specifying what to look for, to be concise and focus on whole pieces of knowledge. For example, *You're going to take detailed technical notes on what's required to code chatGPT in a python notebook, what kinds of data are used, and the process of building as a whole.*
        User Input:
        {user_query}"""
        response, conversation = self.chat(user_query, conversation)
        return response, conversation

    def get_video_topics(self, video_transcript):
        """
        Parses video transcripts into distinct topics
        :param video_transcript: timestamped transcript of video, with keys: text, start, duration
        :return:
        """
        # format transcript into format:
        # ___s
        # line of text
        # ___s
        # line of text
        # ...
        transcript_string = ""
        for line in video_transcript:
            transcript_string += f"""{line['start']}s
            {line['text']}
            """

        prompt = f"""I want you to chunk a YouTube transcript. Here are the guidelines for how you will chunk the transcript:
            First, organize the text into question-based categories.
            Your output should contain labeled sections that are included in brackets. It should contain a [SEARCH] section summarizing the video topics; this will serve to help the user decide which Youtube video they want to pick. It should also contain several [TOPIC] sections that contain the detailed contents of the video, as well as the corresponding timestamps in the format __m__s.
            
            For example, if I have a YouTube video on how to make chocolate chip cookies, your output could look like this:
            
            [SEARCH]
            This is a chocolate chip cookie recipe video. The recipe allows you to make 5 cookies. It will cover which ingredients you need, how to prepare the cookie dough, and how to bake the cookie dough.
            
            [TOPIC: ingredients used in making cookies]
            73s The ingredients you will need include 1 cup of flour, 3 eggs, 1 cup of chocolate chips, and 1 tablespoon of baking soda. Also, preheat your oven to 350 degrees Fahrenheit.
            
            [TOPIC: how to prepare the chocolate chip cookie dough]
            127s To prepare the chocolate chip cookie dough, mix all of the ingredients in a large bowl until well combined.
            
            [TOPIC: how to bake the chocolate chip cookie dough]
            204s Separate the cookie dough into balls that are one-quarter inch in radius and put them on a baking sheet on a tray. Put the tray into the preheated oven and take it out of the oven after 40 minutes. Enjoy your delicious freshly baked chocolate chip cookies!
            
            Here is the transcript I would like you to chunk: {transcript_string}"""

        # OpenAPI call on 16k!!!
        response = openai.ChatCompletion.create(
            engine="gpt-3.5-turbo-16k",
            prompt=prompt,
        )
        topics_raw = response.choices[0]["message"]["content"]
        # parse topics
        topics = []
        for topic in topics_raw.split("[TOPIC:")[1:]:
            if topic != "":
                topic = topic.split("]")
                timestamp = topic[1].split("s")[0]
                topics.append({
                    "topic": topic[0],
                    "text": topic[1],
                    "startTime": timestamp
                })
        search = topics_raw.split("[SEARCH]")[1].split("[TOPIC:")[0]

        return topics, search

    def get_video_description(self, video_title, video_description):
        """
        Makes a search string for a video based on its title and description
        :param video_title: title of video
        :param video_description: description of video
        :return:
        """
        # TODO: Add OPENAI Prompt
        prompt = f""""""

        response = openai.ChatCompletion.create(
            engine="gpt-3.5-turbo",
            prompt=prompt,
        )

        return response.choices[0]["message"]["content"]

    def get_playlist_search(self, playlist_title, playlist_description):
        """
        Generates search string for a playlist, based on title and description
        :param playlist_title: title of the playlist
        :param playlist_description: description of the playlist
        :return:
        """
        # TODO: Add OPENAI Prompt
        prompt = f""""""
        response = openai.ChatCompletion.create(
            engine="gpt-3.5-turbo",
            prompt=prompt,
        )
        return response.choices[0]["message"]["content"]

    def chat(self, query, conversation):
        """
        Chat with the AI
        :param query: query to send to the AI
        :param conversation: conversation history
        :return:
        """
        conversation.append({"role": "user", "content": query})
        response = openai.ChatCompletion.create(
            engine="gpt-3.5-turbo",
            messages=conversation
        )
        conversation.append({"role": "assistant", "content": response.choices[0]["message"]["content"]})
        return response.choices[0]["message"]["content"], conversation
