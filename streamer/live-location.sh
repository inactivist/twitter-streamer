#!/bin/bash
FEEDMAPPER=~/workspace/feedmapper/mapper
PUMP=$FEEDMAPPER/json-pump.py
STREAMER_OPTS="-l DEBUG"
python streamer.py $STREAMER_OPTS -c dev.ini --location-query="$1" | python $PUMP
