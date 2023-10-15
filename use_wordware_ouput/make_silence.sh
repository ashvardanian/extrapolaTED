#!/bin/bash
# Change the -t parameter for a different duration. It's in seconds.
ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 1 silence.mp3

# Old way; stereo, but we don't want this.
#ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t 1 silence.mp3
