#!/bin/bash
ffmpeg -f concat -safe 0 -i videos.txt -i full_audio.mp3 -vsync vfr -pix_fmt yuv420p kb_video.mp4
