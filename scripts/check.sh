#!/usr/bin/env bash

# Change the Working directory to the scripts location
cd "$(dirname "$0")"

# Jump back to the root
cd ..

. venv/bin/activate

cd episodes/

while true
do
    sleep 30
    python check_status.py
done
