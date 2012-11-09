"""
    Tweepy streaming API StreamListener message recognizers.

    These recognize various types of incoming data based on predefined rules.

    TODO: Probably don't need classes.  Consider refactoring.
"""
import tweepy
import simplejson as json


class MessageRecognizer(object):
    def __init__(self, handler_method):
        self.handler = handler_method

    def match(self, stream_data):
        """Return True if this recognizer matches the incoming stream data."""
        return False

    def handle_message(self, stream_data):
        "Handle the incoming message.  Return False to stop stream processing."
        return self.handler(stream_data)


class MatchAnyRecognizer(MessageRecognizer):
    """Match any stream_data."""
    def match(self, stream_data):
        return True


class DataStartsWithRecognizer(MessageRecognizer):
    def __init__(self, handler_method, starts_with):
        self.starts_with = starts_with
        super(DataStartsWithRecognizer, self).__init__(handler_method)

    def match(self, stream_data):
        return stream_data.startswith(self.starts_with)


class DataContainsRecognizer(MessageRecognizer):
    """A simple string-in-message recognizer.  Matches if a string is anywhere
    in the stream_data body."""
    def __init__(self, handler_method, match_string):
        self.contains_string = match_string
        super(DataContainsRecognizer, self).__init__(handler_method)

    def match(self, stream_data):
        return self.contains_string in stream_data
