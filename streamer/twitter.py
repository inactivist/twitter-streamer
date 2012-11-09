"""Twitter utilities."""
import logging
logger = logging.getLogger(__name__)
import tweepy
from config import *


def post_tweet(status_text, config):
    """Post a tweet to the configured Twitter API account."""
    auth1 = tweepy.OAuthHandler(config['consumer_key'], config['consumer_secret'])
    auth1.set_access_token(config['access_token_key'], config['access_token_secret'])
    api = tweepy.API(auth1)
    try:
        api.update_status(status_text)
    except tweepy.TweepError:
        logger.exception("post_tweet")

