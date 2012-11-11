# Twitter Streamer #
*Twitter Streamer* is a Python command-line utility to dump [Twitter streaming API][streaming-apis] 
[statuses/filter][statuses-filter] method data to stdout.

It began life as a testing tool for [Tweepy][tweepy], and to satisfy my curiosity.
It's currently in an early beta test state, needs testing and improvement. 
(see [Known issues](#known-issues), below)

## Prerequisites ##
You will need:

 1. Python 2.7, [Tweepy][tweepy] and its prerequisites.
 2. Your [Twitter API keys][keys].

Once you have your API keys, edit default.ini, providing the required elements.

    [twitter_api]
    # You must use the keys provided by Twitter for your account.
    consumer_key: YOUR_CONSUMER_KEY
    consumer_secret: YOUR_CONSUMER_SECRET
    access_token_key: YOUR_ACCESS_TOKEN_KEY
    access_token_secret: YOUR_ACCESS_TOKEN_SECRET

## Usage ##
Basic usage:

    python streamer.py [options] "track terms" ...
    
You can print a usage summary by invoking `streamer.py` with the `-h` or `--help` option.

The positional *track* parameter provides one or more [track search terms][parameters-track] for the [Twitter 
*statuses/filter* API][statuses-filter].  Commas denote an *or* relationship, while spaces
denote an *and* relationship.  

You can provide multiple *track* parameters, which will expand the search terms.

Please refer to the [track][parameters-track] documentation for specific limitations and 
usage examples.

## Examples ##
Stream (filter) statuses containing both *car* **and** *dog*:

    python streamer.py "car dog"

Stream statuses containing either *boat* **or** *bike*:

    python streamer.py "boat,bike" 
    
Stream statuses containing (*water* **and** *drink*) *or* (*eat* **and** *lunch*):

    python streamer.py "water drink" "eat lunch"
    
## Output Format ##
The default output mode is to dump the raw stream data status text for each received
element, followed by a newline.

Each raw stream element is expected to be a well-formed JSON object, but at present the
stream elements are not separated by commas, nor is the stream wrapped in a JSON
list.  Therefore, if you expect to parse the output of this program as JSON
data, you will need to process it into well-formed JSON, or take each element as
an independent JSON object rather than treat the stream as a JSON array.
## Experimental Features ##
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
* Needs a bit of cleanup -- obsolete code remains from prior project and should
be refactored or removed.
* General error handling needs work.  
    The current default mode retries the connection with a delay
in the event of most failures; this keeps Streamer running despite network
problems or other errors.  
    If you specify the `--terminate-on-errors` (`-t`) option, Streamer will
    terminate with an error message on errors.  This is a work in progress. 
* Configuration (.ini) file error handling needs work.
    Errors due to misconfiguration probably need better handling and reporting. 
* Log messages go to stderr.

##License##
(MIT License) - Copyright (c) 2012 Exodus Development, Inc.
  
[streaming-apis]: https://dev.twitter.com/docs/streaming-apis
[parameters-track]: https://dev.twitter.com/docs/streaming-apis/parameters#track 
[statuses-filter]: https://dev.twitter.com/docs/api/1.1/post/statuses/filter
[keys]: https://dev.twitter.com/docs/faq#7447
[tweepy]: https://github.com/tweepy/tweepy
[twitter-tweets]: https://dev.twitter.com/docs/platform-objects/tweets
