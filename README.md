Twitter Streamer is a command-line utility to dump [Twitter streaming API][1] data
to stdout.  It uses the [statuses/filter][3] method.

It started out as a testing tool for [Tweepy][tweepy].

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
You can get a usage summary by invoking streamer.py with the -h or --help option.

    $ python streamer.py --help
    usage: streamer.py [-h] [-c CONFIG_FILE] [-l LOG_LEVEL] [-r REPORT_LAG]
                       [-u USER_LANG] [-n] [-f FIELDS]
                       track [track ...]
    
    Twitter Stream dumper v0.0.1
    
    positional arguments:
      track                 Status keywords to be tracked.
    
    optional arguments:
      -h, --help            show this help message and exit
      -c CONFIG_FILE, --config-file CONFIG_FILE
      -l LOG_LEVEL, --log-level LOG_LEVEL
                            set log level to one used by logging module. Default
                            is WARN.
      -r REPORT_LAG, --report-lag REPORT_LAG
                            Report time difference between local system and
                            Twitter stream server time exceeding this number of
                            seconds.
      -u USER_LANG, --user-lang USER_LANG
                            BCP-47 language filter(s). If set, incoming status
                            user's language must match these languages.
      -n, --no-retweets     If set, don't include statuses identified as retweets.
      -f FIELDS, --fields FIELDS
                            List of fields to output as CSV columns. If not set,
                            output raw status text, a large JSON structure.


The positional *track* parameter provides one or more [track search terms][2] for the Twitter 
*statuses/filter* API.  Commas denote an *or* relationship, while spaces
denote an *and* relationship.  

You can provide multiple *track* parameters, which will expand the search terms.

Please refer to the [track][2] documentation for specific limitations and 
usage examples.

## Examples ##
Filter statuses containing both *car* **and** *dog*:
    python streamer.py "car dog"

Filter statuses containing either *boat* **or** *bike*:
    python streamer.py "boat,bike" 
    
Filter statuses containing (*water* **and** *drink*) *or* (*eat* **and** *lunch*):
    python streamer.py "water drink" "eat lunch"
    

## Output Format ##
The normal output mode is to dump the raw stream data text for each received
stream element, followed by a newline.

Each raw stream element is a well-formed JSON object, but at present the
stream elements are not separated by commas, nor is the stream wrapped in a JSON
list.  Therefore, if you expect to parse the output of this program as JSON
data, you will need to preprocess it in order to be well-formed JSON.  You should
be able to split the output on newlines, inserting commas between records. 

## Experimental Features ##
 
The *-f* or *--fields=* parameter allows a comma-separated list of output fields.
The field values will be emitted in the order listed in the given *-f* or *--fields=*
parameter.  The output is not formatted in any other way.

Example 1: list created_at and text fields for 'elections'
    python streamer.py -f "created_at,text" elections

Example results:
    2012-11-09 20:26:47 Volatility the Likely Outcome of Elections http://t.co/trmmSpXp #Barron's
    2012-11-09 20:26:50 @WHLive then why the president ordered Boeing to release the layoff news AFTER the elections?

Example 2: list user.name and text fields for tweets containing dogs *and* cats
    python streamer.py -f "user.name,text" "dogs cats"
    
Example Results:
    User name 1,Cats and dogs in Mexico. http://t.co/gYJvhdvv
    User name 2,I actually like both cats and dogs but I've been an introvert for about 27 years now.
    
[1]: https://dev.twitter.com/docs/streaming-apis
[2]: https://dev.twitter.com/docs/streaming-apis/parameters#track 
[3]: https://dev.twitter.com/docs/api/1.1/post/statuses/filter
[keys]: https://dev.twitter.com/docs/faq#7447
[tweepy]: https://github.com/tweepy/tweepy
