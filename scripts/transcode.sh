#!/usr/bin/env bash

cd "$(dirname "$0")"

############
# FFMPEG command
##########
# x264 is used because it is widely supported and the encoder is very fast
# level 4.1 is used because many hardware decoders do not support 4.2 or 5.0
# crf 24 gives pretty good quality but also a big file size.  Good for local streaming
# yadif command scales down to 720p to match my TV resolution
# libfdk_aac is th best aac encoder
# Downmix to stereo
# THe audio filters send the center channel sound (usually dialog) equally to the left and right channels so you can still hear dialog during action movies
# hls is very widely supported and relatively simple
# hls_time 10 - the chromecast only has a 20s buffer so setting this number higher than 10 is problematic
# event mode tells the playlist to start at the beginning and also allows instructs clients to start at the beginning of the playlist. not the middle. 


ffmpeg -i "$1" \
    -c:v copy \
    -c:a libopus -ac 2 -b:a 128k \
    ../library/Friends/$( basename $1 ).mp4



