
import os
from flask import Flask
from flask import render_template
from flask import send_from_directory
from flask import jsonify
from flask import request
from flask import make_response

from castcontroller import client, Command

import socket
import random

import time

# Only these file types are considered "episodes". Anything else (.nfo, .srt,
# sub-directories, cover art, ...) must never be enqueued on the Chromecast.
VIDEO_EXTENSIONS = ('.mp4', '.mkv', '.webm', '.avi', '.mov', '.m4v')


def _library_path(app):
    return os.path.abspath(os.path.join(app.root_path, "..", "library"))


def _list_shows(app):
    """Return the sub-directory names of the library, or [] if unavailable."""
    libpath = _library_path(app)
    try:
        entries = os.listdir(libpath)
    except OSError:
        return []
    return sorted(
        f for f in entries
        if os.path.isdir(os.path.join(libpath, f))
    )


def _video_files(show_path):
    """Return only playable video files in a show directory (sorted)."""
    try:
        names = os.listdir(show_path)
    except OSError:
        return []
    return sorted(
        n for n in names
        if n.lower().endswith(VIDEO_EXTENSIONS)
        and os.path.isfile(os.path.join(show_path, n))
    )


def _base_url():
    """Absolute base URL the Chromecast should fetch episodes from."""
    try:
        host = socket.gethostbyname(socket.gethostname())
        return "http://" + host + ":8080"
    except OSError:
        # Name resolution failed; fall back to the URL the client used.
        return "http://" + request.host


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    def no_store(resp):
        """Mark a response as non-cacheable.

        State-changing commands must never be replayed out of the HTTP cache
        by a browser (e.g. iOS bfcache / standalone-app restore re-issuing the
        previous request).
        """
        resp = make_response(resp)
        resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
        resp.headers['Pragma'] = 'no-cache'
        resp.headers['Expires'] = '0'
        return resp

    @app.route('/')
    @app.route('/html')
    def main():
        libpath = _library_path(app)

        error = None
        if not os.path.isdir(libpath):
            error = "Library folder not found: " + libpath

        shows = _list_shows(app)

        try:
            devices = sorted(client({"cmd": Command.find_devs}))
        except Exception as exc:  # noqa: BLE001 - show a clear page error
            devices = []
            error = "Could not discover Chromecast devices: %s" % (exc,)

        return no_store(render_template(
            'main.html',
            shows=shows,
            devices=devices,
            error=error,
        ))

    @app.route('/library/<path:filename>')
    def library(filename):
        return send_from_directory(_library_path(app) + "/", filename)

    @app.route('/show/<name>/<int:count>/<device>', methods=['POST'])
    def show(name, count, device):
        # Play a random selection of episodes.

        # Send the "stop" command in the event something is already playing.
        client({
            "cmd": Command.stop,
            "device": device
        })

        # NOTE: the Flask dev server used here (see run.sh) may be
        # single-threaded, so this wait blocks other requests. Keep the wait to
        # preserve playback semantics: the device needs a moment to stop before
        # the new episodes are queued.
        time.sleep(3)

        show_path = os.path.join(_library_path(app), name)
        eps = _video_files(show_path)

        if not eps:
            return no_store(jsonify(
                ok=False,
                error="No playable video files found for '%s'" % name
            )), 404

        if len(eps) > count:
            i = random.randrange(len(eps) - count + 1)
            selection = eps[i:i + count]
        else:
            # If not, select the entire episode list.
            selection = eps

        # First episode will NOT be enqueued, but the remaining ones will be.
        base = _base_url()
        enqueue = False
        for e in selection:
            client({
                "device": device,
                "cmd": Command.play,
                "args": [
                    base + "/library/" + name + "/" + e,
                    'video/mp4',
                    enqueue
                ]
            })
            enqueue = True

        return no_store(jsonify(ok=True))

    # TODO Add Next button

    @app.route('/volume/<int:level>/<device>', methods=['POST'])
    def volume(level, device):
        client({
            "cmd": Command.volume,
            "device": device,
            "args": [level]
        })
        return no_store(jsonify(ok=True))

    @app.route('/stop/<device>', methods=['POST'])
    def stop(device):
        client({
            "cmd": Command.stop,
            "device": device
        })
        return no_store(jsonify(ok=True))

    return app
