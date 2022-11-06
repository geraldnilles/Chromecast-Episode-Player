
import os
from flask import Flask
from flask import render_template
from flask import send_from_directory

from castcontroller import client, Command

import socket
import random

import time

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    @app.route('/')
    @app.route('/html')
    def main():
        libdirs = []
        libpath = os.path.abspath( app.root_path+"/../library" )
        for f in os.listdir( libpath ):
            if os.path.isdir( os.path.join( libpath,f ) ):
                libdirs.append( f )

        devices = sorted(client({"cmd":Command.find_devs}))
        return render_template('main.html', shows=libdirs ,devices=devices )

    @app.route('/library/<path:filename>')
    def library(filename):
        return send_from_directory(app.root_path+"/../library/",filename)

    @app.route('/show/<name>/<int:count>/<device>',methods=['GET'])
    def show(name,count,device):
        # Play a random selection of episodes

        # Send the "stop" command in the event something is already playing
        client({
            "cmd":Command.stop,
            "device":device
            })
        time.sleep(3)
        
        show_path = os.path.join(os.path.abspath( app.root_path+"/../library" ),name)
        eps = sorted(os.listdir(show_path))

        if len(eps) > count:
            i = random.randrange(len(eps)-count+1)
            selection = eps[i:i+count]
        else:
            """
            If not, select the entire epsidoe list
            """
            selection = eps

        # First episode will NOT be enqueued, but the remaining ones will be
        # enqueued
        enqueue = False
        for e in selection:
            client({
                "device":device, 
                "cmd":Command.play, 
                "args":[
                    "http://"+socket.gethostbyname(socket.gethostname())+":8080/library/"+name+"/"+e, 
                    'video/mp4',
                    enqueue ]
                })
            enqueue = True

        return "Playing some episodes"

    # TODO Add Next button

    @app.route('/volume/<int:level>/<device>',methods=['GET'])
    def volume(level,device):
        client({
            "cmd":Command.volume,
            "device":device,
            "args":[level]
            })
        return "Adjusting the volume"


    @app.route('/stop/<device>',methods=['GET'])
    def stop(device):
        client({
            "cmd":Command.stop,
            "device":device
            })
        return "Stopping Playback"

    return app



