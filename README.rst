###########################
 Chromecast Episode Player
###########################

This is a simple flask app the lets you select a TV show from your video
library, and randomly queues up a block of episodes to play

Setup
=====

I am lazy and hardcoded a lot of paths.  To ensure success, load this flask app
in the /opt 

Setup the venv::

    python -m venv venv
    . venv/bin/activate
    pip install flask pychromecast


Softlink the systemd service files to you systemd folder

Softlink TV episode folders into the `library` folder


