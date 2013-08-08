# Twitter Streamer #
*Twitter Streamer* is a Python command-line utility to dump [Twitter streaming API][streaming-apis]
[statuses/filter][statuses-filter] method data to stdout.

It began life as a testing tool for [Tweepy][tweepy], and to satisfy my curiosity.
It's currently in an early beta test state, and needs testing and improvement.
(see [Known issues](#known-issues), below)

## Prerequisites ##
You will need:

 1. Python 2.7, [Tweepy][tweepy] and its prerequisites.
 2. Your [Twitter API keys][twitter-api-keys].

Once you have your API keys, export the following environment variables:

    export CONSUMER_KEY="your-consumer-key"
    export CONSUMER_SECRET="your-consumer-secret"
    export ACCESS_KEY="your-access-token"
    export ACCESS_SECRET="your-access-token-secret"

These environment variables must be set correctly for twitter-streamer to
function properly.  If any of these variables are not available, you'll see
an error message and twitter-streamer will terminate.

If you try to use invalid API keys, you'll see something like this output:

    StreamListener.on_error: 401
    StreamListener.on_error: 401
    StreamListener.on_error: 401
    ...

## Usage ##
Basic usage:

    python streamer.py [options] "track terms" ...

You can print a usage summary by invoking `streamer.py` with the `-h` or `--help` option.

The positional *track* parameter provides one or more [track search terms][parameters-track] for the [Twitter
*statuses/filter* API][statuses-filter].  Commas denote an *or* relationship, while spaces
denote an *and* relationship.

You can provide multiple *track* parameters, which will expand the search terms.

Please refer to the [track][parameters-track] documentation for specific limitations and
usage examples.  See [this question][twitter-track-hashtags] for help filtering on hashtags using
URL encoding.

## Examples ##
Stream (filter) statuses containing both *car* **and** *dog*:

    $ python streamer.py "car dog"

Stream statuses containing either *boat* **or** *bike*:

    $ python streamer.py "boat,bike"

Stream statuses containing (*water* **and** *drink*) *or* (*eat* **and** *lunch*):

    $ python streamer.py "water drink" "eat lunch"

## Output Format ##
The default output mode dumps the unprocessed stream's JSON string for each received
element, followed by a newline.

Each raw stream element is expected to be a well-formed JSON object, but the
stream elements are not separated by commas, nor is the stream wrapped in a JSON
list.  Therefore, if you expect to parse the entire output of this program's JSON
data, you will need to transform it into well-formed JSON, or take each newline-separated
element as an independent JSON object rather than treat the stream as a JSON array.

The program will produce CSV output when using `--fields` (`-f`) field specifiers.
See [*Field Output Selectors*](#field-output-selectors), below.
## Experimental Features ##
### Following users ###
As of v0.0.6-dev, you can follow user ids by using the `--follow` (`-F`) option.
The `--follow` option accepts a list of comma-separated integer user id values.

I plan to add user `screen_name` lookup at some point, in the meantime,
you can use the helper script `scripts/lookup-users.py`:

    $ python scripts/lookup-users.py twitter,tweepy
    tweepy: 14452478
    twitter: 783214

(Please keep in mind that per the Streaming API docs, following users does not
filter results to only those users, rather, it adds the selected users' streams
to the incoming stream results.)

### Location-based searching ###
As of v0.0.4, you can add location-based search criteria by specifying the `--locations`
option.  The value is a comma-separated list of longitude, latitude pairs that
define one or more bounding boxes to include in the stream.  (This implies that
the number of comma-separated `--location=` values must be a multiple of 4, and
in fact Tweepy enforces this for us.)

Example:

    $ python streamer.py -f=place.full_name,coordinates.coordinates,text --locations="-122.75,36.8,-121.75,37.8"

This produces a stream of status updates as CSV, with the `place.full_name`,
`coordinates.coordinates`, and `text` fields (if available).  Here is
an example with longitude and latitude obscured in order to protect privacy:

    "San Jose, CA","[longitude, latitude]",@user is a boy
    "Oakland, CA","[longitude, latitude]",@user1 @user2 @user3 @user4 @user5 We are all 1 big happy family #BELIEBERS that what we are 24/7 were #STRONG
    "California, US",,i'll be here awhile #311

where `longitude` and `latitude` are floating-point numbers representing Twitter's
notion of the Tweet's location.

There are several fields that are used to determine location: [`coordinates`][twitter-coordinates],
[`place`][twitter-place], and `geo` (the latter is deprecated.)  Note that
Twitter prioritizes the location data by preferring `coordinates` over `place` when
determining if a tweet should be included based on geo location.

Note that including `--locations`
parameter will not further filter other search terms (such as `track` keywords)
-- per the [location][parameters-location] reference, it acts as an OR when
combined with `track` keywords.

See the Twitter's [Tweets][twitter-tweets] structure reference for more information
about location-based information, and the [location][parameters-location] for more
about the `location` parameter.

#### Location Query ####
Recent development versions (0.0.5-dev and higher) support a new option:
`--location-query`.  It allows you to reference a Twitter Place name, and
automatically use the resulting coordinates as the value of the `--location`
parameter.  (Currently the resulting `--location-query` bounding box overrides
any values passed in the `--location` command line option)

The `--location-query` value is passed to the Tweepy `API.geo_search` method
(which uses the Twitter [geo/search][twitter-go-search]) as the `query` parameter.

The value is case-insensitive, and the value must match an existing Twitter Place
`full_name` field.  In general, you can use this pattern:

     --location-query="{city-name}, {state-abbrev}"
     --location-query="{state-name}, US"

where {city-name} is a well-known city name, {state-name} is a full state name,
and {state-abbrev} is a standard two-letter state abbreviation.  You can search
for other types of names, but you'll have to do you own research or experiment
to find valid values.

Example:

    --location-query="San Jose, CA"
    --location-query="California, US"

Matching is done without regard to spaces, but
the Twitter API might fail to return expected matches if you deviate too far from the
pattern shown above.  If in doubt, enable full debug logging, by passing
`-l DEBUG` on the command line.

#### Location Issues ####
* Note that there are [open issues](https://dev.twitter.com/issues/295) regarding
the accuracy of Twitter's `locations` filtering.  You may need to do your own
post-filtering of the results to ensure they are within the desired bounding
box.
* Using `--location-query="United States"` results in an error because [Twitter
doesn't return a bounding box for the United States][lookup-usa].  It does for
[Canada][lookup-canada].  Go figure.

### Field Output Selectors ###
The `-f` (or `--fields`) parameter allows a comma-separated list of output fields.
The field values will be emitted in the order listed in the given `-f`
parameter value.  Output will be formatted as CSV records.

You can access nested elements by using dotted notation: `user.name` accesses
the `name` element of the `user` object.  See Twitter's [tweets][twitter-tweets]
structure reference for a list of valid elements.

If you reference a non-existent element, the output column will be empty.
If you prefer to have an error message displayed and terminate processing
specify the `-t` or `--terminate-on-error` option.

Example 1: *list created_at and text fields for 'elections'*

    python streamer.py -f "created_at,text" elections

Example results:

    2012-11-09 20:26:47 Volatility the Likely Outcome of Elections http://t.co/trmmSpXp #Barron's
    2012-11-09 20:26:50 @WHLive then why the president ordered Boeing to release the layoff news AFTER the elections?

Example 2: *list user.name and text fields for tweets containing dogs *and* cats*

    python streamer.py -f "user.name,text" "dogs cats"

Example Results:

    User name 1,Cats and dogs in Mexico. http://t.co/gYJvhdvv
    User name 2,I actually like both cats and dogs but I've been an introvert for about 27 years now.

## To be done ##
See TODO.md
## Known issues ##
* Needs a bit of cleanup -- obsolete code remains from prior project and will
be refactored or removed.
* Error handling needs work.
    The current default mode retries the connection with a delay
in the event of most failures; this keeps Streamer running despite network
problems or other errors.
    If you specify the `--terminate-on-errors` (`-t`) option, Streamer will
    terminate with an error message on errors rather than retrying certain
    operations.  This is a work in progress.
* Log messages go to stderr.
* If you receive 401 errors during authentication, ensure your system's date and
time settings are correct.  [Auth can fail if your clock is out of sync][twitter-401-error] with
Twitter's servers.  The `scripts/twitter-time-compare.sh` script shows
Twitter's server and the local server times for comparison.


##License##
(MIT License) - Copyright (c) 2012-2013 Exodus Development, Inc. except where
otherwise noted.  Please refer to LICENSE.md for the gory details.

[streaming-apis]: https://dev.twitter.com/docs/streaming-apis
[parameters-track]: https://dev.twitter.com/docs/streaming-apis/parameters#track
[statuses-filter]: https://dev.twitter.com/docs/api/1.1/post/statuses/filter
[twitter-api-keys]: https://dev.twitter.com/docs/faq#7447
[tweepy]: https://github.com/tweepy/tweepy
[twitter-tweets]: https://dev.twitter.com/docs/platform-objects/tweets
[parameters-location]: https://dev.twitter.com/docs/streaming-apis/parameters#locations
[twitter-place]: https://dev.twitter.com/docs/platform-objects/places
[twitter-coordinates]: https://dev.twitter.com/docs/platform-objects/tweets#obj-coordinates
[twitter-401-error]: https://dev.twitter.com/discussions/6778
[twitter-geo-search]: https://dev.twitter.com/docs/api/1/get/geo/search
[lookup-usa]: http://api.twitter.com/1/geo/id/96683cc9126741d1.json
[lookup-canada]: http://api.twitter.com/1/geo/id/3376992a082d67c7.json
[twitter-track-hashtags]: https://dev.twitter.com/discussions/7483
