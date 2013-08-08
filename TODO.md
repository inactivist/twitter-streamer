## Capture Time Limits ##
Set a time limit (elapsed time) for capture.  End capture after that time expires.
Perhaps useful for capturing data for later playback (testing.)

Implemented in development branch as of commit [d01a6997bbfea9f03a5a638947299916c8d48f31](https://github.com/inactivist/twitter-streamer/commit/d01a6997bbfea9f03a5a638947299916c8d48f31)


## Tweepy ##
* Update requirements.txt to refer to a more recent stable version of Tweepy.

### Alternatives ###
* Explore alternative Twitter libraries, such as [Twython][twython] or
  [PTT][ptt]

  Why? Tweepy's maintainer has indicated lack of time to push Tweepy
  forward.  Tweepy's a bit more complicated than we need it to be.  I'd
  like something more lightweight.

## Unit tests ##
We have some.  We need *more*.

## Additional streaming API parameter support ##
* Location-based filtering using [locations] parameter. (Implemented in v0.0.4
and later.)
* User-based filtering using [follow] parameter.

## Additional streaming API methods support ##
More than just `statuses/filter`.

## Improve character encoding support ##
Twitter uses UTF-8, or so I've read.  Current code tries to encode fields as UTF-8 if
possible.  Needs testing/verification.

## Improve output formatting options ##

### Slicing ###
Allow field output slice notation?

    -f "text[:20]"

would output the first 20 characters of the 'text' field.

### Custom field output handlers ###
Example: Ability to emit true/false for a given field based on presence.

For example, `retweeted_status` is only present
if a status is a retweet of another status message, and if present, it's
a fully-baked Tweepy `Status` model instance.  So, if you want to emit a boolean
flag indicating whether an item is a retweet, it would be nice to be able to do
so based on whether the named field exists.

As a general case, if we could specify an output formatter function from a list of
allowed formatters, we could do something like: `field_name:output_formatter_func`
where `output_formatter_func` represents the name of a known and permitted
callable that results in a string.

Or, we could just pass in a formatting string...

Examples:

    python streamer.py -f "retweeted_status:bool,text"

would result in `bool(retweeted_status)` being used as the output value.

    python streamer.py -f "retweeted_status%s,text"

would result in '%s' being used as a format string for the `retweeted_status` field.

##Configuration via environment variables##
Dump the config file stuff.  Use environment variables, make them compatible with
Tweepy's [tests.py](https://github.com/tweepy/tweepy/blob/master/tests.py) example.

This has been implemented in development branch as of v0.0.6-dev commit [c6bd79666d8dd404a8303bab29cb5542f92c50da](https://github.com/inactivist/twitter-streamer/commit/c6bd79666d8dd404a8303bab29cb5542f92c50da)


[locations]: https://dev.twitter.com/docs/streaming-apis/parameters#locations
[follow]: https://dev.twitter.com/docs/streaming-apis/parameters#follow
[twython]: https://twython.readthedocs.org/en/latest/
[ptt]: https://github.com/sixohsix/twitter