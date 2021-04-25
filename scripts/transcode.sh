#!/usr/bin/env bash

lib_dir="$(dirname "$0")/../library/"

############
# FFMPEG command
##########
# This command will transcode all of the files in the provided directory into
# an mp4.  It will assume the video does not need to be transcoded and can be
# copied.  It will also transode the audio into a stero opus stream which works
# on Chromecast


newdir=$( realpath "$lib_dir/$( basename "$1" )" )
rm -r "$newdir"
mkdir "$newdir"

echo "$newdir"


for x in $( ls "$1" )
do


    in=$( realpath "$1/$x" )
    echo $in

    out=$( realpath "$newdir/${x%.*}.mp4" )
    echo $out

    ffmpeg -i "$in" \
        -c:v copy \
        -c:a libopus -ac 2 -b:a 128k \
        "$out"
   
    sleep 2
done




