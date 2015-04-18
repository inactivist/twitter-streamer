import argparse

def csv_args(value):
    """Parse a CSV string into a Python list of strings.

    Used in command line parsing."""
    return map(str, value.split(","))


def csv_ints(value):
    """ Parse a CSV string into an array of ints. """
    return map(int, value.split(","))


def userids_type(value):
    """ Alias for csv_args.  Parse list of userids into array of strings. """
    return csv_args(value)


def locations_type(value):
    """Conversion and validation for --locations= argument."""
    parsed = csv_args(value)
    if len(parsed) % 4 != 0:
        raise argparse.ArgumentTypeError('must contain a multiple of four floating-point numbers defining the locations to include.')
    return parsed


def duration_type(value):
    """
    Parse 'duration' type argument.
    Format: {number}{interval-code}
    where: number is an integer
    interval-code: one of ['h', 'm', 's'] (case-insensitive)
    interval-code defaults to 's'
    Returns # of seconds.
    """
    import re
    value = value.strip() + ' ' # pad with space which is synonymous with 'S' (seconds).
    secs = { ' ': 1, 's': 1, 'm': 60, 'h': 3600, 'd': 86400 }
    match = re.match("^(?P<val>\d+)(?P<code>[\ssmhd]+)", value.lower())
    if match:
        val = int(match.group('val'))
        code = match.group('code')
        if not code:
            # Default is seconds (s)
            code = 's'
        else:
            code = code[0]
        return val * secs[code]
    else:
        raise argparse.ArgumentTypeError('Unexpected duration type "%s".' % value.strip())


def parse_command_line(version):
    parser = argparse.ArgumentParser(description='Twitter Stream dumper v%s' % version)

    parser.add_argument(
        '-f',
        '--fields',
        type=csv_args,
        metavar='field-list',
        help='list of fields to output as CSV columns.  If not set, raw status text (all fields) as a large JSON structure.')

    parser.add_argument(
        '-F',
        '--follow',
        type=userids_type,
        metavar='follow-userid-list',
        help='comma-separated list of Twitter userids (numbers, not names) to follow.'),

    parser.add_argument(
        '--locations',
        type=locations_type,
        metavar='bounding-box-coordinates',
        help='a list of comma-separated bounding boxes to include.  See Tweepy streaming API location parameter documentation.')

    # TODO: Accept lists of place names (multiple arguments)
    # Example: --location-query=usa --location-query=Canada
    # Construct a list of bounding boxes; pass to Twitter.
    parser.add_argument(
        '--location-query',
        metavar='location-full-name',
        help=r"""query Twitter's geo/search API to find an exact match for provided
         name, which is then converted to a locations bounding box and used as
         the --location parameter."""
        )

    parser.add_argument(
        '-d',
        '--duration',
        type=duration_type,
        metavar='duration-spec',
        help='capture duration from first message receipt.'
        ' Use 5 or 5s for 5 seconds, 5m for 5 minutes, 5h for 5 hours, or 5d for 5 days.'
    )

    parser.add_argument(
        '-m',
        '--max-tweets',
        metavar='count',
        type=int,
        help='maximum number of statuses to capture.'
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
        Incoming status user\'s language must match one these languages;
        if you wish to capture all languages,
        use -u '*'."""
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

    p = parser.parse_args()
    # HACK: If user specifies wildcard '*' language filter in list,
    # empty the user_lang member so we don't filter on them later.
    # See: StreamListener.tweet_matchp()
    if  p.user_lang and '*' in p.user_lang:
        p.user_lang = []

    return p
