#!/bin/bash

## This bash script calls a python script which outputs picamera
## output to stdout. then pipes that through ffmpeg to stream
## to YouTube.
## calls raspivid
## pipes to ffmpeg

## YouTube Settings - that really shouldn't be in here!
RTMP_URL=rtmp://a.rtmp.youtube.com/live2
STREAM_KEY=9b39-du7r-rrt5-5d0a
## perhaps take that as an arguement?

while :
  do
  ## start the camera
  python3 startCameraStream-h264.py | /usr/local/bin/ffmpeg -re -ar 44100 -ac 2 -acodec pcm_s16le -f s16le -ac 2 -i /dev/zero -f h264 -i - -vcodec copy -acodec aac -ab 128k -g 50 -strict experimental -f flv $RTMP_URL/$STREAM_KEY
  sleep 2
done
