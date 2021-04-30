
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

    # Start the Chromecast Controller THread
    with app.app_context():
        controller.init()

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

    @app.route('/show/<name>',methods=['GET'])
    def rewind(name="Friends"):
        # TODO Check if a show is aleady in the queue and dont add.
        controller.q.put(["show",name])
        return "Playing some episodes"

    @app.route('/volume/<int:level>',methods=['GET'])
    def forward(level=30):
        controller.q.put(["volume",level])
        return "Adjusting the volume"


    @app.route('/stop',methods=['GET'])
    def stop():
        controller.q.put(["stop",None])
        return "Stopping Playback"

    @app.route('/reset',methods=['GET'])
    def reset():
        controller.q.put(["reset",None])
        return "Refreshing"

    #from . import api
    #app.register_blueprint(api.bp)

    return app



