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
import logging
logger = logging.getLogger(__name__)
import simplejson as json

TWITTER_TIME_FORMAT = '%a %b %d %H:%M:%S +0000 %Y'
MAX_SLEEP_TIME = 1

def parse_twitter_time(time_str):
    return datetime.datetime.strptime(time_str, TWITTER_TIME_FORMAT)

def datetime_to_unixtime(dt):
    return time.mktime(dt.timetuple())


def datetime_to_twitter_time_string(dt):
    # Convert datetime to "Wed Aug 27 13:08:45 +0000 2008" format.
    return dt.strftime(TWITTER_TIME_FORMAT)


def _init_logger(level):
    from logging import _checkLevel
    FORMAT = "%(asctime)-15s %(message)s"
    logging.basicConfig(format=FORMAT)
    logger.setLevel(level)


_init_logger("WARNING")
last_time = None
start_time = datetime.datetime.utcnow()

for line in sys.stdin:
    if not line.strip():
        # Line is empty, continue.
        logger.debug('Line is empty, continuing...')
        continue
    try:
        status = json.loads(line)
    except json.JSONDecodeError as e:
        logger.warn("Error parsing line '%s', continuing", line)
        continue
    except Exception as e:
        logger.exception('Fatal error parsing %s.', line)
        sys.exit(1)

    # If first item, emit it immediately.
    # Else, calculate time delta from last status and delay the appropriate amount of time,
    # if any is required.
    if not last_time:
        last_time = parse_twitter_time(status.get('created_at'))
    else:
        # get time delta in seconds.
        current = parse_twitter_time(status.get('created_at', last_time))
        delta = current - last_time
        sleep_time = delta.total_seconds()
        if sleep_time < 0 or sleep_time > MAX_SLEEP_TIME:
            sys.stderr.write(
                "sleep_time (%d) outside bounds for tweet id %s\n" % (
                    sleep_time,
                    status.get('id_str')))
            sys.stderr.flush()
        # Clamp sleep_time to 0 <= sleep_time <= MAX_SLEEP_TIME
        sleep_time = max(0, min(sleep_time, MAX_SLEEP_TIME))
        last_time = current
        time.sleep(sleep_time)

    logger.debug('replay: Writing line: %s', line[:30])
    sys.stdout.write(line)
    sys.stdout.flush()