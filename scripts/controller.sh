#!/usr/bin/env bash

# Change the Working directory to the scripts location
cd "$(dirname "$0")"

# Jump back to the root
cd ..

if [[ -f venv ]]
then
	. venv/bin/activate
fi

rm instance/cast_socket

python episodes/controller.py

