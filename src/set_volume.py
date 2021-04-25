#!/usr/bin/env python

import sys

import pychromecast
import time

from threading import Lock

mutex = Lock()

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

controller = cast.socket_client.receiver_controller


print(controller.status.volume_level)
cast.set_volume(0.5)


def cb_fun(status):
    print(controller.status.volume_level)

controller.update_status(cb_fun)

time.sleep(1)

