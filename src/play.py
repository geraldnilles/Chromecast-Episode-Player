#!/usr/bin/env python

import sys
import os

#curr_dir = os.path.dirname(os.path.realpath(__file__))
#sys.path.insert(0,curr_dir+"/lib")

#import netifaces

import pychromecast
import time

chromecasts = pychromecast.get_chromecasts()[0]

cast = None 
for c in chromecasts:
    if c.device.friendly_name == "Bedroom TV":
    #if c.device.friendly_name == "Living Room TV":
        cast = c

if cast == None:
    print ("Chromecast Not Found!")
    exit(-1)

cast.wait()

mc = cast.media_controller
# Use my custom App ID so i can debug on the chromecast
#mc.app_id = "AE70FB75"

#mc.play_media("http://10.0.0.200:9312/out.m3u8?r="+str(time.time()),'application/x-mpegURL')
#mc.play_media("http://10.0.0.200:9312/out.m3u8",'application/x-mpegURL', stream_type="LIVE")
#mc.play_media("http://10.0.0.200:9312/out.m3u8",'application/x-mpegURL')
#mc.play_media("http://10.0.0.200:9312/dash_out.mpd",'application/dash+xml')
mc.play_media("http://10.0.0.200:8312/Friends/0601.mkv.mp4",'video/mp4')
#mc.play_media("http://10.0.0.200:9312/out.webm",'video/webm')
mc.block_until_active()

time.sleep(10)
mc.play()

time.sleep(10)

mc.play_media("http://10.0.0.200:8312/Friends/0602.mkv.mp4",'video/mp4', enqueue=True)
mc.play_media("http://10.0.0.200:8312/Friends/0603.mkv.mp4",'video/mp4', enqueue=True)
