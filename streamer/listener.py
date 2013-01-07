import sys
import time
import csv as csv_lib
import tweepy
import simplejson as json

import message_recognizers
import utils

MISSING_FIELD_VALUE = ''


class StreamListener(tweepy.StreamListener):
    """
    Tweepy StreamListener that dumps tweets to stdout.
    """

    def __init__(self, opts, logger, api=None):
        super(StreamListener, self).__init__(api=api)
        self.opts = opts
        self.csv_writer = csv_lib.writer(sys.stdout)
        self.running = True
        self.first_message_received = None
        self.status_count = 0
        self.logger = logger

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

            message_recognizers.DataContainsRecognizer(
                handler_method=self.on_disconnect,
                match_string='"disconnect":'),

            # Everything else is sent to logger
            message_recognizers.MatchAnyRecognizer(
                handler_method=self.on_unrecognized),
        )

    def dump_with_timestamp(self, text, category="Unknown"):
        print "(%s)--%s--%s" % (category, datetime.datetime.now(), text)

    def dump_stream_data(self, stream_data):
        self.dump_with_timestamp(stream_data)

    def on_unrecognized(self, stream_data):
        self.logger.warn("Unrecognized: %s", stream_data.strip())

    def on_disconnect(self, stream_data):
        msg = json.loads(stream_data)
        self.logger.warn("Disconnect: code: %d stream_name: %s reason: %s",
                    utils.resolve_with_default(msg, 'disconnect.code', 0),
                    utils.resolve_with_default(msg, 'disconnect.stream_name', 'n/a'),
                    utils.resolve_with_default(msg, 'disconnect.reason', 'n/a'))

    def parse_warning_and_dispatch(self, stream_data):
        try:
            warning = json.loads(stream_data).get('warning')
            return self.on_warning(warning)
        except json.JSONDecodeError:
            self.logger.exception("Exception parsing: %s" % stream_data)
            return False

    def parse_status_and_dispatch(self, stream_data):
        """
        Process an incoming status message.
        """
        status = tweepy.models.Status.parse(self.api, json.loads(stream_data))
        if self.tweet_matchp(status):
            self.status_count += 1
            if self.should_stop():
                self.running = False
                return False

            if self.opts.fields:
                try:
                    csvrow = []
                    for f in self.opts.fields:
                        try:
                            value = utils.resolve_with_default(status, f, None)
                        except AttributeError:
                            if self.opts.terminate_on_error:
                                self.logger.error("Field '%s' not found in tweet id=%s, terminating." % (f, status.id_str))
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
                        # See: tweepy.utils.convert_to_utf8_str() for example conversion.
                        try:
                            value = value.encode('utf8')
                        except AttributeError:
                            pass
                        csvrow.append(value)
                    self.csv_writer.writerow(csvrow)
                except UnicodeEncodeError as e:
                    self.logger.warn(f, exc_info=e)
                    pass
            else:
                # Raw JSON stream data output:
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
                self.logger.warn("Tweet time and local time differ by %d seconds", delta.seconds)

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
        self.logger.warn("Warning: code=%s message=%s" % (warning['code'], warning['message']))
        # If code='FALLING_BEHIND' buffer state is in warning['percent_full']

    def on_error(self, status_code):
        self.logger.error("StreamListener.on_error: %r" % status_code)
        if status_code != 401:
            self.logger.error(" -- stopping.")
            # Stop on anything other than a 401 error (Unauthorized)
            # Stop main loop.
            self.running = False
            return False

    def on_timeout(self):
        """Called when there's a timeout in communications.

        Return False to stop processing.
        """
        self.logger.warn('on_timeout')
        return  ## Continue streaming.

    def on_data(self, data):
        if not self.first_message_received:
            self.first_message_received = int(time.time())

        if self.should_stop():
            self.running = False
            return False # Exit main loop.

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

    def should_stop(self):
        """
        Return True if processing should stop.
        """
        if self.opts.duration:
            if self.first_message_received:
                et = int(time.time()) - self.first_message_received
                flag = et >= self.opts.duration
                if flag:
                    self.logger.debug("Stop requested due to duration limits (et=%d, target=%d seconds).",
                                 et,
                                 self.opts.duration)
                return flag
        if self.opts.max_tweets and self.status_count > self.opts.max_tweets:
            self.logger.debug("Stop requested due to count limits (%d)." % self.opts.max_tweets)
            return True
        return False
