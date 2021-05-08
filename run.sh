#!/usr/bin/env bash

cd "$(dirname "$0")"

. venv/bin/activate


cleanup(){
    echo "Cleaning up Background Jobs"
    kill -s INT $( jobs -pr )
    sleep 2
    echo "Checking if there are other background jobs"
    jobs -pr


}

trap 'cleanup' INT

# Start the controller in a separate process
python episodes/controller.py &

export FLASK_APP=episodes
export FLASK_ENV=development

flask run -p 8765 --host=0.0.0.0 


