
import os
from flask import Flask
from flask import render_template
from flask import send_from_directory
from . import controller

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        HISTORY=os.path.join(app.instance_path, 'history.json'),
        DATABASE=os.path.join(app.instance_path, 'todos.json'),
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Start the Chromecast Controller THread
    with app.app_context():
        controller.init()

    @app.route('/')
    def main(name=None):
        return render_template('main.html', name=name)

    @app.route('/library/<path:filename>')
    def library(filename):
        return send_from_directory(app.root_path+"/../library/",filename)

    @app.route('/rewind/<int:t_skip>',methods=['GET'])
    def rewind(t_skip=30):
        controller.q.put(["rewind",t_skip])
        return "Rewind"

    @app.route('/forward/<int:t_skip>',methods=['GET'])
    def forward(t_skip=30):
        controller.q.put(["forward",t_skip])
        return "Fast Forward"


    @app.route('/reset',methods=['GET'])
    def reset():
        controller.q.put(["reset",None])
        return "Resetting Chrome Connection"

    #from . import api
    #app.register_blueprint(api.bp)

    return app



