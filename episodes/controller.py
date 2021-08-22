#!/usr/bin/env python

import time
import os
import random

from datetime import datetime

#DEFAULT_CHROMECAST_NAME = "Living Room TV"
DEFAULT_CHROMECAST_NAME = "Bedroom TV"


# Put the socket into the instance folder
UNIX_SOCKET_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),"..","instance","cast_socket")

class ChromecastNotFound(Exception):
    pass


class Controller:

    def __init__(self,name = DEFAULT_CHROMECAST_NAME):
        self.name = name;
        self.chromecasts = None 
        self.device = None

        self.zconf = zeroconf.Zeroconf()

        self.browser = pychromecast.discovery.CastBrowser(pychromecast.discovery.SimpleCastListener(self.cast_add, self.cast_remove, self.cast_update), self.zconf)
        self.browser.start_discovery()

    def cast_add(self, uuid, _service):
        print("New Cast Found:",uuid)
        self.cast_parse(uuid)

    def cast_remove(self, uuid, _service, cast_info):
        print("Removing Cast:",uuid)
        if self.browser.devices[uuid].friendly_name != self.name:
            return
        info = self.browser.devices[uuid]
        print (info.friendly_name,"Removed")
        self.device = None
        

    def cast_update(self, uuid, _service):
        print("Updating Cast:",uuid)
        self.cast_parse(uuid)

    def cast_parse(self,uuid):
        if self.browser.devices[uuid].friendly_name != self.name:
            return

        info = self.browser.devices[uuid]

        print (info.friendly_name,"Updated")
        self.device =  pychromecast.get_chromecast_from_cast_info(info,self.zconf)
        self.device.wait()
        print (info.friendly_name,"is ready")
    
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
        rc = self.device.socket_client.receiver_controller

        # If Backdrop is the current app, the TV is likely off.  Temporarily
        # launch the media reciever in order to wake up the TV before launching
        # the show
        if rc.status.app_id == pychromecast.config.APP_BACKDROP:
            rc.launch_app(pychromecast.config.APP_MEDIA_RECEIVER)
            time.sleep(15)
        
        # Quit the current app before starting the show
        self.device.quit_app()
        time.sleep(5)

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
        self.device.quit_app()

    def parse_command(self,cmd):
        # If device is None, that means no chromecast was detected.  We will
        # not attempt to execute any commands
        if self.device == None:
            print ("Chromecast Not Connected. Ingoring Command")
            return
            
        if cmd[0] == "reset":
            print("Reconnectig to Chromecast...")
            self.reset()
            print("Ready")
            return

        if cmd[0] == "stop":
            self.stop()
            print("Stopping")
            return

        if cmd[0] == "status":
            self.check_status()
            print("Checking Status")
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

    with Listener(UNIX_SOCKET_PATH , authkey=b'secret password') as listener:

        while True:
            with listener.accept() as conn:
                cmd = conn.recv()
                print(repr(cmd))
                try:
                    c.parse_command(cmd)
                except pychromecast.error.NotConnected:
                    print ("Connection Lost. Clearing Connection")
                    c.device = None
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
    main()
    """
    while True:
        try:
            main()
        except pychromecast.error.NotConnected:
            print ("Chromecast Disconnected - Resetting the Controller worker")
        except ChromecastNotFound:
            print ("Cannot find a chromecast. Sleeping 60 second before retrying")
            time.sleep(60)
    """

def cleanup(*args):
    print("Exiting gracefully")
    exit(0)
    

if __name__ == "__main__":
    import signal
    import pychromecast
    import zeroconf
    signal.signal(signal.SIGINT, cleanup)

    main_disconnect_wrapper()

