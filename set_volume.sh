#!/usr/bin/env bash

cd "$(dirname "$0")"

. venv/bin/activate

cd src 

python set_volume.py

