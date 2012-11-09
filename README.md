Twitter Streamer is a command-line utility to dump [Twitter streaming API][1] data
to stdout.  It uses the [statuses/filter][3] method.

NOTE: Output formats are lame and will change at some point soon.

    usage: streamer.py [-h] [-c CONFIG_FILE] [-l LOG_LEVEL] [-v] [-r REPORT_LAG]
                       [-u USER_LANG] [-i] [-f FIELD]
                       track [track ...]

The *track* parameters provides [track search terms][2] for the Twitter 
statuses/filter API.  Commas denote an *or* relationship, while spaces
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

Each element is a well-formed JSON object, but at present the
stream elements are not separated by commas, nor is the stream wrapped in a JSON
list.  Therefore, if you expect to parse the output of this program as JSON
data, you will need to preprocess it in order to be well-formed JSON.  You should
be able to split the output on newlines, inserting commas between records. 

## Experimental Features ##
 
The *-f* or *--field=* option allows a comma-separated list of output fields.
The field values will be emitted in the order listed in the given *-f* or *--field=*
parameter.  The output is not formatted in any other way.

Example:
    python streamer.py -f created_at,text elections

Example results:
    2012-11-09 20:26:47 Volatility the Likely Outcome of Elections http://t.co/trmmSpXp #Barron's
    2012-11-09 20:26:50 @WHLive then why the president ordered Boeing to release the layoff news AFTER the elections?

[1]: https://dev.twitter.com/docs/streaming-apis
[2]: https://dev.twitter.com/docs/streaming-apis/parameters#track 
[3]: https://dev.twitter.com/docs/api/1.1/post/statuses/filter
