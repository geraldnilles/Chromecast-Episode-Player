#!/usr/bin/env python

import time
import os
import random
import logging

from datetime import datetime

#DEFAULT_CHROMECAST_NAME = "Living Room TV"
DEFAULT_CHROMECAST_NAME = "Bedroom TV"
    
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


# Put the socket into the instance folder
UNIX_SOCKET_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),"..","instance","cast_socket")

class ChromecastNotFound(Exception):
    pass


class Controller:

    def __init__(self,name = DEFAULT_CHROMECAST_NAME):
        self.name = name;
        self.chromecasts = None 
        self.device = None

        self.zconf = None

        self.browser = None
        self.fail_counter = 0
        self.zconf_reset()
        self.age = 0

    def zconf_reset(self):
        logging.info("Resetting ZeroConf Browser")
        if self.zconf != None:
            logging.warning("Closing Zconf")
            self.zconf.close()
            logging.warning("Zconf Closed")
            time.sleep(5)

        logging.info("Starting Zconf")
        self.zconf = zeroconf.Zeroconf()

        logging.info("Starting Browser")
        self.browser = pychromecast.discovery.CastBrowser(pychromecast.discovery.SimpleCastListener(self.cast_add, self.cast_remove, self.cast_update), self.zconf)
        self.browser.start_discovery()
        logging.info("ZeroConf Started")

    def cast_add(self, uuid, _service):
        logging.info("New Cast Found: "+str(uuid))
        self.cast_parse(uuid)

    def disconnect(self, dev=-1):
        if time.time()-self.age < 30:
            return
        if dev == -1:
            dev = self.device
        if dev != None:
            logging.info("Disconnecting Chromecast")
            dev.disconnect(5)
            logging.info("Disconnected")


    def cast_remove(self, uuid, _service, cast_info):
        logging.info("Removing Cast: "+str(uuid))
        if self.browser.devices[uuid].friendly_name != self.name:
            return
        info = self.browser.devices[uuid]
        self.disconnect()
        

    def cast_update(self, uuid, _service):
        logging.info("Updating Cast: "+str(uuid))
        self.cast_parse(uuid)

    def cast_parse(self,uuid):
        if self.browser.devices[uuid].friendly_name != self.name:
            return

        
        info = self.browser.devices[uuid]

        logging.info(str(info.friendly_name)+" Updated")
        
        # Backup Old Device
        oldDevice = self.device
        # Clear existing connections before we move forward
        # Get New Device
        newDevice =  pychromecast.get_chromecast_from_cast_info(info,self.zconf)
        newDevice.wait(15)
        logging.info(str(info.friendly_name)+" is ready")
        # When new device is ready, set the self variable
        self.device = newDevice
        # And disconnect the old device assuming they are not the same
        if oldDevice != newDevice:
            self.disconnect(oldDevice)
            time.sleep(1)

        self.fail_counter = 0

        self.device.wait(15)
        self.check_status()
        # Set the timestamp the connection was last setup
        self.age = time.time()
    
    def reset(self):
        if not self.device.is_idle:
            self.device.quit_app()
            time.sleep(5)
    

    def volume(self,level):
        rc = self.device.socket_client.receiver_controller
        # If no status is set, bail and let the user try again later
        if rc.status == None:
            logging.warning("Status Not Set.  Bailing")
            self.check_status()
            return

        prev = rc.status.volume_level

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
            logging.info("Volume now set to "+str(rc.status.volume_level))
        rc.update_status(cb_fun)

    def check_status(self):
        rc = self.device.socket_client.receiver_controller
        def cb_fun(status):
            logging.debug("Current App: " + repr(rc.status.app_id))
            logging.debug("Chromecast Status: " + repr(rc.status))
        rc.update_status(cb_fun)
        

    def show(self,name, num):
        rc = self.device.socket_client.receiver_controller


        # If status is not set, abort and let the user try again
        # This is done to avoid an error while we wait for the system to recover
        # Idealy, id use the status callback function to send the show when ready
        if rc.status == None:
            logging.warning("Status Not Set.  Bailing")
            self.check_status()
            return
            
        # If Backdrop is the current app, the TV is likely off.  Temporarily
        # launch the media reciever in order to wake up the TV before launching
        # the show
        if rc.status.app_id == pychromecast.config.APP_BACKDROP:
            rc.launch_app(pychromecast.config.APP_MEDIA_RECEIVER)
            time.sleep(15)
        
        # Quit the current app before starting the show
        self.device.quit_app()
        time.sleep(5)

        logging.info("Playing "+ str(name))
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
                logging.info ("Queueing up "+e)
                mc.play_media("http://arch-episodes.lan:8080/library/"+name+"/"+e,
                                'video/mp4', enqueue=enqueue)
            else:
                logging.info ("Starting with "+e)
                mc.play_media("http://arch-episodes.lan:8080/library/"+name+"/"+e,
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
            logging.error("Chromecast Not Connected. Ingoring Command")
            self.fail_counter += 1
            logging.info("Fail Counter increased to %d"%(self.fail_counter))

            if self.fail_counter > 5:
                logging.error("Killing after 5 bad")
                assert EOFError

            return
            
        if cmd[0] == "reset":
            logging.info("Reconnectig to Chromecast...")
            self.reset()
            return

        if cmd[0] == "stop":
            self.stop()
            logging.info("Stopping")
            return

        if cmd[0] == "status":
            self.check_status()
            logging.debug("Checking Status")
            return

        if cmd[0] == "volume":
            self.volume(cmd[1]) 
            logging.info("Adjusting Volume")
            return

        if cmd[0] == "show":
            self.show(cmd[1], cmd[2]) 
            logging.info("Starting a Show")
            return


def main():
    from multiprocessing.connection import Listener
    c = Controller()

    with Listener(UNIX_SOCKET_PATH , authkey=b'secret password') as listener:

        while True:
            with listener.accept() as conn:
                cmd = conn.recv()
                logging.debug(repr(cmd))
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

