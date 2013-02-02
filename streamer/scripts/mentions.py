"""
    Collect mentions from twitter-streamer output stream.
    Output is simple CSV:
      tweet_id, tweeter_id, tweeter_screen_name, mentioned_user_id, mentioned_user_screen_name
"""
import sys
import os
import logging
logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get('LOGGING_LEVEL', 'DEBUG'))
import simplejson as json


def dump_mentions(t):
    try:
        m = t['entities']['user_mentions']
        ou = t['user']
        for u in m:
            #print m, u
            print ','.join([t['id_str'], ou['id_str'], ou['screen_name'], u['id_str'], u['screen_name']])
    except KeyError:
        # No entities, skip this item.
        pass

for line in sys.stdin:
    try:
        t = json.loads(line.strip())
        dump_mentions(t)
    except json.JSONDecodeError:
        logger.error('Error decoding %s' % line[:40])
        pass