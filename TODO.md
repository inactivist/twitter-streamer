* Unit tests.
* Improve character encoding support.  Twitter uses UTF-8, or so I've read.
* Better output formatting options.
* Field selection options: would be nice to be able to emit true/false for a 
field based on presence.  For example, `retweeted_status` is only present 
if a status is a retweet of another status message, and if present, it's
a fully-baked Tweepy `Status` model instance.  So, if you want to emit a boolean
flag indicating whether an item is a retweet, it would be nice to be able to do
so based on whether the named field exists.
    As a general case, we could do something like: `field_name:output_formatter_func`
    where `output_formatter_func` represents the name of a known and permitted 
    callable that results in a string.
    
    Or, we could just pass in a formatting string... 
    Examples: 
        `-f "retweeted_status:bool,text"` would result in `bool(retweeted_status)` being
        used as the output value.
        
        `-f "retweeted_status%s,text"` would result in '%s' being used as a 
        format string for the `retweeted_status` field. 
