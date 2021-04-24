#!/usr/bin/env bash

. venv/bin/activate

export FLASK_APP=episodes
export FLASK_ENV=development

flask run -p 8765 --host=0.0.0.0


