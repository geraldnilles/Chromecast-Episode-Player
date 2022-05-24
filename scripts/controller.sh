#!/usr/bin/env bash

# Change the Working directory to the scripts location
cd "$(dirname "$0")"

# Jump back to the root
cd ..

. venv/bin/activate

rm instance/cast_socket

python3 episodes/controller.py

