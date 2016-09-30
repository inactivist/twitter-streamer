import os
import sys
import logging
import time
import datetime
import tweepy
import simplejson as json
import utils

import args
from listener import StreamListener

logger = logging.getLogger(__name__)

RETRY_LIMIT = 10

"""
    List of named location query (--location-query) names and their
    associated bounding boxes (longitude, latitude) (what is the name of that standard?  geoJSON?)

    Recursive lookups:
    If a value is string, it's a reference to a named entry in the table.  Use the remainder of the
    value string as the new lookup key.
"""
LOCATION_QUERY_MACROS = {
    'any': [-180,-90,180,90],
    'all': 'any',
    'global': 'any',
    'usa': [-124.848974,24.396308,-66.885444,49.384358], # http://www.openstreetmap.org/?box=yes&bbox=-124.848974,24.396308,-66.885444,49.384358
    'contintental_usa': 'usa'
}


def lookup_location_query_macro(name):
    """
    Look up location query name in macro table.
    Return list of coordinates of bounding box as floating point numbers, or None if
    not found.
    """
    resolved = LOCATION_QUERY_MACROS.get(name.lower())
    if isinstance(resolved, basestring):
        return lookup_location_query_macro(resolved)
    return resolved



def get_version():
    from __init__ import __version__
    return __version__


def location_query_to_location_filter(tweepy_auth, location_query):
    t = lookup_location_query_macro(location_query)
    if t:
        return t
    api = tweepy.API(tweepy_auth)
    # Normalize whitespace to single spaces.
    places = api.geo_search(query=location_query)
    normalized_location_query = location_query.replace(' ', '')
    for place in places:
        logger.debug('Considering place "%s"' % place.full_name)
        # Normalize spaces
        if place.full_name.replace(' ', '').lower() == normalized_location_query.lower():
            logger.info('Found matching place: full_name=%(full_name)s id=%(id)s url=%(url)s' % place.__dict__)
            if place.bounding_box is not None:
                t = [x for x in place.bounding_box.origin()]
                t.extend([x for x in place.bounding_box.corner()])
                logger.info('  location box: %s' % t)
                return t
            else:
                raise ValueError("Place '%s' does not have a bounding box." % place.full_name)

    # Nothing found, try for matching macro
    raise ValueError("'%s': No such place." % location_query)


def make_filter_args(opts, tweepy_auth):
    kwargs = {}
    if opts.track:
        kwargs['track'] = opts.track
    if opts.stall_warnings:
        kwargs['stall_warnings'] = True
    if opts.locations:
        kwargs['locations'] = map(float, opts.locations)
    if opts.location_query:
        kwargs['locations'] = location_query_to_location_filter(tweepy_auth, opts.location_query)
    if opts.follow:
        kwargs['follow'] = opts.follow
    return kwargs


def process_tweets(opts):
    """Set up and process incoming streams."""
    try:
        auth = tweepy.OAuthHandler(os.environ['CONSUMER_KEY'], os.environ['CONSUMER_SECRET'])
        auth.set_access_token(os.environ['ACCESS_KEY'], os.environ['ACCESS_SECRET'])
    except KeyError as e:
        logger.error('You must set the %s API key environment variable.', e)
        return

    logger.debug('Init tweepy.Stream()')
    logger.debug(opts)
    listener = StreamListener(opts=opts, logger=logger)
    streamer = tweepy.Stream(auth=auth, listener=listener, retry_count=9999,
        retry_time=1, buffer_size=16000)

    try:
        kwargs = make_filter_args(opts, auth)
    except ValueError as e:
        listener.running = False
        sys.stderr.write("%s: error: %s\n" % (__file__, e.message))
        return

    while listener.running:
        try:
            try:
                logger.debug('streamer.filter(%s)' % kwargs)
                streamer.filter(**kwargs)
            except TypeError as e:
                if 'stall_warnings' in e.message:
                    logger.warn("Installed Tweepy version doesn't support stall_warnings parameter.  Restarting without stall_warnings parameter.")
                    del kwargs['stall_warnings']
                    streamer.filter(**kwargs)
                else:
                    raise

            logger.debug('Returned from streaming...')
        except IOError:
            if opts.terminate_on_error:
                listener.running = False
            logger.exception('Caught IOError')
        except KeyboardInterrupt:
            # Stop the listener loop.
            listener.running = False
        except Exception:
            listener.running = False
            logger.exception("Unexpected exception.")

        if listener.running:
            logger.debug('Sleeping...')
            time.sleep(5)



if __name__ == "__main__":
    import config
    opts = args.parse_command_line(get_version())

    # TODO: Fix this -
    if (opts.location_query is None and
        opts.locations is None and
        opts.follow is None):
        if not opts.track:
            sys.stderr.write('%s: error: Must provide list of track keywords if --location or --location-query is not provided.\n' % __file__)
            sys.exit()
    utils.init_logger(logger, opts.log_level)
    process_tweets(opts)
