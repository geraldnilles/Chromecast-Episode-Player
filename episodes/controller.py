#!/usr/bin/env python

import time
import os
import random

from datetime import datetime

#DEFAULT_CHROMECAST_NAME = "Living Room TV"
DEFAULT_CHROMECAST_NAME = "Bedroom TV"

# Put the socket into the instance folder
UNIX_SOCKET_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),"..","instance","cast_socket")

class Controller:

    def __init__(self):
        self.chromecasts = None 
        self.device = None
    
    def find_devices(self):
        print ("Looking for Chromecasts")
        chromecasts , browser = pychromecast.get_listed_chromecasts( friendly_names=[DEFAULT_CHROMECAST_NAME]  )
        if not chromecasts:
            print ("No Chromecast Found")
            self.device = None
        else:
            print ("Chromecast Found")
            self.device = chromecasts[0]
        browser.stop_discovery()


    def reset(self):
        if not self.device.is_idle:
            self.device.quit_app()
            time.sleep(5)
    

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

    def check_status(self):
        rc = self.device.socket_client.receiver_controller
        def cb_fun(status):
            print ("Chromecast Status: ",rc.status)
        rc.update_status(cb_fun)
        

    def show(self,name, num):
        print ("Playing ", name)
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

        if len(eps) > num:
            i = random.randrange(len(eps)-num+1)
            sel = eps[i:i+num]

        # We want the first video to be nromal. and all subsequent videos be
        # enqueued
        # TODO Dynamically look up the local IP address
        enqueue = False
        for e in sel:
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
                time.sleep(2)



    def stop(self):
        mc = self.device.media_controller
        mc.stop()

    def parse_command(self,cmd):
        if cmd[0] == "reset":
            print("Reconnectig to Chromecast...")
            self.find_devices()
            self.device.wait()
            self.reset()
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
            self.show(cmd[1], cmd[2]) 
            print("Starting a Show")
            return


def main():
    from multiprocessing.connection import Listener
    c = Controller()
    c.find_devices()
    c.device.wait()

    with Listener(UNIX_SOCKET_PATH , authkey=b'secret password') as listener:

        while True:
            with listener.accept() as conn:
                cmd = conn.recv()
                print(repr(cmd))
                c.parse_command(cmd)
                conn.send("OK")


# This is a function can be used by clients on other machines to send messages
# to this controller
def sendMsg(obj):
    from multiprocessing.connection import Client
    with Client(UNIX_SOCKET_PATH , authkey=b'secret password') as conn:
        conn.send(obj) 
        resp = conn.recv()
        return resp

# Main Error Handling Wrapper
#
# This while loop will restart the main loop whenever there is an "normal
# error".  For example, if the wifi goes down for a few minutes and the
# chromecast becomes unreachable, this will restart it
def main_disconnect_wrapper():
    print("Starting Persistent Chromecast Worker")
    while True:
        try:
            main()
        except pychromecast.error.NotConnected:
            print ("Chromecast Disconnected - Resetting the Controller worker")

def cleanup(*args):
    print("Exiting gracefully")
    exit(0)
    

if __name__ == "__main__":
    import signal
    import pychromecast
    signal.signal(signal.SIGINT, cleanup)

    main_disconnect_wrapper()

