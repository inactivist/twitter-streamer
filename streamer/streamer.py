#!/usr/bin/env python

import logging
import os
import sys
import time

import tweepy

from . import args
from . import location
from . import utils
from .listener import StreamListener

logging.basicConfig()
logger = logging.getLogger(__name__)

RETRY_LIMIT = 10


def get_version():
    from .__init__ import __version__

    return __version__


def make_filter_args(opts, tweepy_auth):
    kwargs = {}
    if opts.track:
        kwargs["track"] = opts.track
    if opts.stall_warnings:
        kwargs["stall_warnings"] = True
    if opts.locations:
        kwargs["locations"] = list(map(float, opts.locations))
    if opts.location_query:
        kwargs["locations"] = location.location_query_to_location_filter(
            tweepy_auth, opts.location_query
        )
    if opts.follow:
        kwargs["follow"] = opts.follow
    return kwargs


def process_tweets(opts):
    """Set up and process incoming streams."""
    try:
        consumer_key = os.environ["CONSUMER_KEY"]
        consumer_secret = os.environ["CONSUMER_SECRET"]
        access_key = os.environ["ACCESS_KEY"]
        access_secret = os.environ["ACCESS_SECRET"]
        logger.debug(
            "consumer_key={consumer_key}, consumer_secret={consumer_secret}".format(
                **locals()
            )
        )
        logger.debug(
            "access_key={access_key}, access_secret={access_secret}".format(**locals())
        )
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
    except KeyError as e:
        logger.error("You must set the %s API key environment variable.", e)
        return

    logger.debug("Init tweepy.Stream()")
    logger.debug(opts)
    listener = StreamListener(opts=opts, logger=logger)
    streamer = tweepy.Stream(
        auth=auth, listener=listener, retry_count=9999, retry_time=1, buffer_size=16000
    )

    try:
        kwargs = make_filter_args(opts, auth)
    except ValueError as e:
        listener.running = False
        sys.stderr.write("%s: error: %s\n" % (__file__, e.message))
        return

    while listener.running:
        try:
            try:
                logger.debug("streamer.filter(%s)", kwargs)
                streamer.filter(**kwargs)
            except TypeError as e:
                if "stall_warnings" in e.message:
                    logger.warn(
                        "Installed Tweepy version doesn't support stall_warnings parameter.  Restarting without stall_warnings parameter."
                    )
                    del kwargs["stall_warnings"]
                    streamer.filter(**kwargs)
                else:
                    raise

            logger.debug("Returned from streaming...")
        except IOError:
            if opts.terminate_on_error:
                listener.running = False
            logger.exception("Caught IOError")
        except KeyboardInterrupt:
            logger.warning("KeyboardInterrupt")
            # Stop the listener loop.
            listener.running = False
        except Exception:
            listener.running = False
            logger.exception("Unexpected exception.")

        if listener.running:
            logger.debug("Sleeping...")
            time.sleep(5)


if __name__ == "__main__":
    opts = args.parse_command_line(get_version())

    # TODO: Fix this -
    if not (opts.location_query or opts.locations or opts.follow):
        if not opts.track:
            sys.stderr.write(
                "%s: error: Must provide list of track keywords if --location, --location-query, or --follow arguments are not provided.\n"
                % __file__
            )
            sys.exit()
    utils.init_logger(logger, opts.log_level)
    logger.debug("opts=%s", opts.__dict__)
    process_tweets(opts)
