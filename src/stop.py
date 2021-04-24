#!/usr/bin/env python

import sys

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

cast.quit_app()



