"""
Replay tweets from stdin (or a file) with a fixed delay,
or by examining timestamps on original tweets and using a delay delta
based on time between last and next tweet.

How to do continuous play if coming from stdin?
Or is that only possible if coming from a named file?
 - http://mail.python.org/pipermail/tutor/2003-May/022520.html
"""
import sys
import time
import datetime
import simplejson as json

def parse_twitter_time(time_str):
    return datetime.datetime.strptime(time_str, '%a %b %d %H:%M:%S +0000 %Y')


def datetime_to_unixtime(dt):
    return time.mktime(dt.timetuple())


start_time = None
for line in sys.stdin:
    status = json.loads(line)
    if start_time:
        pass
    else:
        # Get start time from first status.
        start_time = parse_twitter_time(status.get('created_at'))
        print start_time
        print datetime_to_unixtime(start_time)
        sys.exit()