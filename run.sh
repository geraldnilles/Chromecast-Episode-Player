#!/usr/bin/env bash

cd "$(dirname "$0")"

. venv/bin/activate


export FLASK_APP=episodes
export FLASK_ENV=development

flask run -p 8080 --host=0.0.0.0 

