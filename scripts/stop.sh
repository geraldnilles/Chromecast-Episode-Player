#!/usr/bin/env bash

cd "$(dirname "$0")"

cd ..

. venv/bin/activate

cd src 

python stop.py

