#!/usr/bin/env bash

# Change the Working directory to the scripts location
cd "$(dirname "$0")"

# Jump back to the root
cd ..

if [[ -f venv ]]
then
	. venv/bin/activate
fi

cd episodes/

while true
do
    sleep 30
    python check_status.py
done

