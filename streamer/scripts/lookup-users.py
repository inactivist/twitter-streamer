import os
import sys
import tweepy

consumer_key = os.environ['CONSUMER_KEY']
consumer_secret = os.environ['CONSUMER_SECRET']
access_key = os.environ['ACCESS_KEY']
access_secret = os.environ['ACCESS_SECRET']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)


def lookup_user_ids(api, screen_names):
    """ Return screen names converted to user ids. """
    # Replace any ids starting with '@' with the resulting user id.
    l = api.lookup_users(screen_names=screen_names)
    # Order of returned items may not match order of arguments.
    return dict(zip([(x.screen_name, x.id_str) for x in l], [x.id_str for x in l]))


user_ids = lookup_user_ids(api, sys.argv[1:])
for user_name, user_id in user_ids:
    print "%s: %s" % (user_name, user_id)