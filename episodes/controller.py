#!/usr/bin/env python

import time
import pychromecast
import threading
import queue

q = queue.Queue()

class Controller:

    def __init__(self):
        self.chromecasts = None 
        self.device = None
    
    def find_devices(self):
        self.chromecasts = pychromecast.get_chromecasts()[0]

    def select_device(self,name="Living Room TV"):
        for c in self.chromecasts:
            if c.device.friendly_name == name:
                self.device = c
   
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


    def parse_command(self,cmd):
        if cmd[0] == "reset":
            print("Reconnectig to Chromecast...")
            self.find_devices()
            self.select_device()
            self.device.wait()
            print("Ready")
            return

        if cmd[0] == "forward":
            self.skip(cmd[1]) 
            print("Fast Forward")
            return

        if cmd[0] == "rewind":
            self.skip(-1*cmd[1]) 
            print("Jump Back")
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


def get_queue():
    return q
    

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

