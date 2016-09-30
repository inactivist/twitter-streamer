#!/bin/bash
# Print Twitter server time and local system time for comparison
lynx --head --dump https://api.twitter.com/1/help/test.json | grep Date: ;  echo Date: `date -u +"%a, %d %b %Y %T %z"` '(local system)'
