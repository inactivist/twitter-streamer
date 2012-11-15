import sys
import csv as csv_lib
import logging
import time
import datetime
import tweepy
import simplejson as json
import message_recognizers
import utils

logger = logging.getLogger(__name__)

RETRY_LIMIT = 10
MISSING_FIELD_VALUE = ''


def csv_args(value):
    """Parse a CSV string into a Python list of strings.

    Used in command line parsing."""
    return map(str, value.split(","))

def locations_type(value):
    """Conversion and validation for --locations= argument."""
    parsed = csv_args(value)
    if len(parsed) % 4 != 0:
        raise argparse.ArgumentTypeError('must contain a multiple of four floating-point numbers defining the locations to include.')
    print parsed
    return parsed

def _get_version():
    from __init__ import __version__
    return __version__


def _init_logger(config, opts):
    from logging import _checkLevel
    FORMAT = "%(asctime)-15s %(message)s"
    level = _checkLevel(opts.log_level.upper())
    logging.basicConfig(format=FORMAT)
    logger.setLevel(level)


class StreamListener(tweepy.StreamListener):
    def __init__(self, opts, api=None):
        super(StreamListener, self).__init__(api=api)
        self.opts = opts
        self.csv_writer = csv_lib.writer(sys.stdout)
        self.running = True

        # Create a list of recognizer instances, in decreasing priority order.
        self.recognizers = (
            message_recognizers.DataContainsRecognizer(
                handler_method=self.parse_status_and_dispatch,
                match_string='"in_reply_to_user_id_str":'),

            message_recognizers.DataContainsRecognizer(
                handler_method=self.parse_limit_and_dispatch,
                match_string='"limit":{'),

            message_recognizers.DataContainsRecognizer(
                handler_method=self.parse_warning_and_dispatch,
                match_string='"warning":'),

            #
            # Everything else gets dumped to output...
            message_recognizers.MatchAnyRecognizer(
                handler_method=self.dump_stream_data),
        )

    def dump_with_timestamp(self, text, category="Unknown"):
        print "(%s)--%s--%s" % (category, datetime.datetime.now(), text)

    def dump_stream_data(self, stream_data):
        self.dump_with_timestamp(stream_data)

    def parse_warning_and_dispatch(self, stream_data):
        try:
            self.dump_stream_data(stream_data)
            warning = json.loads(stream_data)['warning']
            return self.on_warning(warning)
        except json.JSONDecodeError as e:
            logger.exception("Exception parsing: %s" % stream_data)
            return False

    def parse_status_and_dispatch(self, stream_data):
        """Parse an incoming status and do something with it.
        """
        status = tweepy.models.Status.parse(self.api, json.loads(stream_data))
        if self.tweet_matchp(status):
            if self.opts.fields:
                try:
                    csvrow = []
                    for f in self.opts.fields:
                        try:
                            value = utils.resolve_with_default(status, f, None)
                        except AttributeError:
                            if opts.terminate_on_error:
                                logger.error("Field '%s' not found in tweet id=%s, terminating." % (f, status.id_str))
                                # Terminate main loop.
                                self.running = False
                                # Terminate read loop.
                                return False
                            else:
                                value = MISSING_FIELD_VALUE
                        # Try to encode the value as UTF-8, since Twitter says
                        # that's how it's encoded. 
                        # If it's not a string value, we eat the exception, 
                        # as value is already set.
                        try:
                            value = value.encode('utf8')
                        except AttributeError:
                            pass
                        csvrow.append(value)
                    self.csv_writer.writerow(csvrow)
                except UnicodeEncodeError as e:
                    logger.warn(f, exc_info=e)
                    pass
            else:
                print stream_data.strip()

        # Parse stream_data, compare tweet timestamp to current time as GMT;
        # This bit does consume some time, so let's not do it unless absolutely 
        # necessary.
        if self.opts.report_lag:
            now = datetime.datetime.utcnow()
            tweepy_status = tweepy.models.Status.parse(self.api, json.loads(stream_data))
            delta = now - tweepy_status.created_at
            if abs(delta.seconds) > self.opts.report_lag:
                # TODO: Gather and report stats on time lag.
                # TODO: Log transitions: lag less than or greater than current
                # # seconds, rising/falling, etc.
                logger.warn("Tweet time and local time differ by %d seconds", delta.seconds)

    def parse_limit_and_dispatch(self, stream_data):
        return self.on_limit(json.loads(stream_data)['limit']['track'])

    def is_retweet(self, tweet):
        return hasattr(tweet, 'retweeted_status') \
            or tweet.text.startswith('RT ') \
            or ' RT ' in tweet.text

    def tweet_matchp(self, tweet):
        """Return True if tweet matches selection criteria...

        Currently this filters on self.opts.lang if it is not nothing...
        """
        if self.opts.no_retweets and self.is_retweet(tweet):
            return False

        if self.opts.user_lang:
            return tweet.user.lang in self.opts.user_lang
        else:
            return True

    def on_warning(self, warning):
        logger.warn("Warning: code=%s message=%s" % (warning['code'], warning['message']))
        # If code='FALLING_BEHIND' buffer state is in warning['percent_full']

    def on_error(self, status_code):
        logger.error("StreamListener.on_error: %r" % status_code)
        if status_code != 401:
            logger.error(" -- stopping.")
            # Stop on anything other than a 401 error (Unauthorized)
            # Stop main loop.
            self.running = False
            return False

    def on_timeout(self):
        """Called when there's a timeout in communications.

        Return False to stop processing.
        """
        logger.warn('on_timeout')
        return  ## Continue streaming.

    def on_data(self, data):
        for r in self.recognizers:
            if r.match(data):
                if r.handle_message(data) is False:
                    # Terminate main loop.
                    self.running = False
                    return False  # Stop streaming
                # Don't execute any other recognizers, and don't call base
                # on_data() because we've already handled the message.
                return
        # Don't execute any of the base class on_data() handlers. 
        return

def location_query_to_location_filter(tweepy_auth, location_query):
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
    return kwargs


def process_tweets(config, opts):
    """Set up and process incoming streams."""
    cfg = config.as_dict().get('twitter_api')
    auth = tweepy.OAuthHandler(cfg.get('consumer_key'), cfg.get('consumer_secret'))
    auth.set_access_token(cfg.get('access_token_key'), cfg.get('access_token_secret'))

    logger.debug('Init tweepy.Stream()')
    logger.debug(opts)
    listener = StreamListener(opts)
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
                    logger.warn('Installed Tweepy version does not support stall_warnings parameter.  Restarting without stall warnings.')
                    streamer.filter(track=track)
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


def _parse_command_line():
    parser = argparse.ArgumentParser(description='Twitter Stream dumper v%s' % _get_version())

    parser.add_argument(
        '-f',
        '--fields',
        type=csv_args,
        metavar='field-list',
        help='list of fields to output as CSV columns.  If not set, raw status text (all fields) as a large JSON structure.')

    parser.add_argument(
        '--locations',
        type=locations_type,
        metavar='bounding-box-coordinates',
        help='a list of comma-separated bounding boxes to include.  See Tweepy streaming API location parameter documentation.')

    parser.add_argument(
        '--location-query',
        metavar='location-full-name',
        help=r"""query Twitter's geo/search API to find an exact match for provided
         name, which is then converted to a locations bounding box and used as
         the --location parameter."""
        )

    parser.add_argument(
        '-c',
        '--config-file',
        metavar='config-file-name',
        default='default.ini',
        help='use configuration settings from the file given in this option.'
        
        )

    parser.add_argument(
        '-l',
        '--log-level',
        default='WARN',
        metavar='log-level',
        help="set log level to one recognized by core logging module.  Default is WARN."
        )

#    parser.add_argument(
#        '-v',
#        '--verbosity',
#        action='count',
#        help='set verbosity level for various operations.  Default is non-verbose output.'
#        )

    parser.add_argument(
        '-r',
        '--report-lag',
        type=int,
        metavar='seconds',
        help='Report time difference between local system and Twitter stream server time exceeding this number of seconds.'
        )

    parser.add_argument(
        '-u',
        '--user-lang',
        type=csv_args,
        default='en',
        metavar='language-code',
        help="""BCP-47 language filter(s).  A comma-separate list of language codes.
        Default is "en", which will include
        only tweets made by users having English (en) as their profile language.
        Incoming status user\'s language must match one these languages."""
        )

    parser.add_argument(
        '-n',
        '--no-retweets',
        action='store_true',
        help='don\'t include statuses identified as retweets.'
        )

    parser.add_argument(
        '-t',
        '--terminate-on-error',
        action='store_true',
        help='terminate processing on errors.')

    parser.add_argument(
        '--stall-warnings',
        action='store_true',
        help='request stall warnings from Twitter streaming API if Tweepy supports them.')

    parser.add_argument(
        'track',
        nargs='*',
        help='status keywords to be tracked (optional if --locations provided.)'
        )

    return parser.parse_args()


if __name__ == "__main__":
    import argparse
    import config
    opts = _parse_command_line()
    
    # TODO: Fix this - 
    if opts.location_query is None and opts.locations is None:
        if not opts.track:
            sys.stderr.write('%s: error: Must provide list of track keywords if --location or --location-query is not provided.\n' % __file__)
            sys.exit()
    conf = config.DictConfigParser()
    conf.read(opts.config_file)
    _init_logger(conf, opts)
    process_tweets(conf, opts)
