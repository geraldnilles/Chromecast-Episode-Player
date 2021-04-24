#!/usr/bin/env bash

cd "$(dirname "$0")"

cd ../library

# TODO Replace with a more common HTTP server...python?
../../Media-Center-2.0/HTTP-Server/node_modules/.bin/http-server --cors -p 8312 -c-1



