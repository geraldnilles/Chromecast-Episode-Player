
import os
from flask import Flask
from flask import render_template
from flask import send_from_directory

from . import controller

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

        return render_template('main.html', shows=libdirs )

    @app.route('/library/<path:filename>')
    def library(filename):
        return send_from_directory(app.root_path+"/../library/",filename)

    @app.route('/show/<name>/<int:count>',methods=['GET'])
    def play(name,count=5):
        # TODO Check if a show is aleady in the queue and dont add.
        controller.sendMsg(["show",name,count])
        return "Playing some episodes"

    @app.route('/volume/<int:level>',methods=['GET'])
    def volume(level=30):
        controller.sendMsg(["volume",level])
        return "Adjusting the volume"


    @app.route('/stop',methods=['GET'])
    def stop():
        controller.sendMsg(["stop",None])
        return "Stopping Playback"

    @app.route('/reset',methods=['GET'])
    def reset():
        controller.sendMsg(["reset",None])
        return "Refreshing"

    #from . import api
    #app.register_blueprint(api.bp)

    return app



