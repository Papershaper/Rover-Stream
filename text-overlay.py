#!/usr/bin/emv python
## This code is intended to add an overlay to the picamera feed
## camera feed is sent to stdout
## output will be piped into ffmpeg for YouTube
## call this code with bash script to encode the h264
## $ ./startPythonStream.sh

import os
import time
import picamera
import sys
from signal import pause
from datetime import datetime

#sys.stdout = os.fdopen(stdout.fileno(), 'wb', 0)

##---------------------------------------------

## start caputuring video

with picamera.PiCamera() as camera:
    camera.resolution = (1280,720)
    camera.framerate = 25
    # camera.annotate_background = picamera.Color('black')
    # camera.start_recording(sys.stdout, bitrate=40000000, format='h264')
    camera.start_preview()
    while True:
        i = datetime.now()
        now = i.strftime('%d %b %Y - %H:%M:%S')
        camera.annotate_text = ' Rover Live Stream - '+now+' '
        #camera.wait_recording(0.2)
        time.sleep(0.2)
