#!/usr/bin/env python

import time
import pychromecast
import threading
import queue
import os
import random


q = queue.Queue()

class Controller:

    def __init__(self):
        self.chromecasts = None 
        self.device = None
    
    def find_devices(self):
        self.chromecasts = pychromecast.get_chromecasts()[0]

    def select_device(self,name="Bedroom TV"):
        for c in self.chromecasts:
            if c.device.friendly_name == name:
                self.device = c
    
    # Probalby wont use this
    """   
    def skip(self,t_seconds):
        mc = self.device.media_controller
        if not mc.status.supports_seek:
            print("App cannot skip.  Ignoring Request")
            return
        def cb_fun(status):
            print("Skipping")
            t_now = mc.status.current_time
            mc.seek(t_now+t_seconds)
            
        mc.update_status(cb_fun)
        print("Refreshing Data")
        
        #t_now = mc.status.current_time
        #mc.seek(t_now+t_seconds)
    """

    def volume(self,level):
        rc = self.device.socket_client.receiver_controller
        prev = rc.status.volume_level
        print ("Volume currently set to ",rc.status.volume_level)

        # Special Cases: 1 will be mean step volume down 5%.  
        #                2 will mean volume up 5%
        #                Anything else will be interpreted as a percentage

        if (level == 1):
            # Down 5%
            level = prev - 0.05
        elif (level == 2):
            # Up 5%
            level = prev + 0.05
        else:
            level = level/100.0
            
        rc.set_volume(level)

        def cb_fun(status):
            print ("Volume now set to ",rc.status.volume_level)
        rc.update_status(cb_fun)

    def show(self,name):
        print ("Playing ", name)
        num = 3
        mc = self.device.media_controller

        # Get the aboslute path
        lib_path = os.path.abspath(
            # Jump back 1 directory and into the selcted show folder
            os.path.join(
                # Strip out the basename
                os.path.dirname(
                    # Path of current file
                    os.path.abspath(__file__)
                )
            ,"..","library",name )
            )
        try:
            eps = os.listdir(lib_path)
        except:
            print("Show was not found")
            eps = []

        # TODO Sort the episodes by name

        # If number of library episodes is more than "num", then randomly
        # select a chunk of sequential episodes

        if len(eps) > num
            i = random.randrange(len(eps)-num+1)
            eps = eps[i:i+num]

        # We want the first video to be nromal. and all subsequent videos be
        # enqueued
        # TODO Dynamically look up the local IP address
        enqueue = False
        for e in eps:
            if enqueue:
                print ("Queueing up ",e)
                mc.play_media("http://10.0.0.200:8765/library/"+name+"/"+e,
                                'video/mp4', enqueue=enqueue)
            else:
                print ("Starting with ",e)
                mc.play_media("http://10.0.0.200:8765/library/"+name+"/"+e,
                                'video/mp4', enqueue=enqueue)
                mc.block_until_active(10)
                enqueue = True



    def stop(self):
        self.device.quit_app()

    def parse_command(self,cmd):
        if cmd[0] == "reset":
            print("Reconnectig to Chromecast...")
            self.find_devices()
            self.select_device()
            self.device.wait()
            print("Ready")
            return

        if cmd[0] == "stop":
            self.stop()
            print("Stopping")
            return

        if cmd[0] == "volume":
            self.volume(cmd[1]) 
            print("Adjusting Volume")
            return

        if cmd[0] == "show":
            self.show(cmd[1]) 
            print("Starting a Show")
            return


def worker():
    c = Controller()
    c.find_devices()
    c.select_device()
    c.device.wait()
    while True:
        cmd = q.get()
        c.parse_command(cmd)
        q.task_done()


def init():
    threading.Thread(target=worker, daemon=True ).start()

# TODO Remove this
#def get_queue():
#    return q
    

if __name__ == "__main__":

    c = Controller()
    c.find_devices()
    c.select_device()
    c.device.wait()
    time.sleep(5)
    for x in range(10):
        time.sleep(20)
        print("Seek")
        c.ff_30sec()

