## Unit tests ##
We need some.

Need to collect a test data set for unit testing, and devise a method of feeding
the test data set to Streamer.

## Additional streaming API parameter support ##
* Location-based filtering using [locations] parameter.
* User-based filtering using [follow] parameter. 

## Additional streaming API methods support ##
More than just `statuses/filter`.   
## Improve character encoding support ##
Twitter uses UTF-8, or so I've read.  Current code tries to encode fields as UTF-8 if 
possible.  Needs testing/verification.

## Better output formatting options ##

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


[locations]: https://dev.twitter.com/docs/streaming-apis/parameters#locations
[follow]: https://dev.twitter.com/docs/streaming-apis/parameters#follow
