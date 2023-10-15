#!/bin/bash
echo ffmpeg -i $1 -vf "scale=8000:-1,zoompan=z='min(zoom+0.0015,1.5)':x='if(gte(zoom,1.5),x,x+1)':y='y':d=$2" -c:v libx264 $3
ffmpeg -i $1 -vf "scale=8000:-1,zoompan=z='min(zoom+0.0004,4.5)':x='if(gte(zoom,1.5),x,x+1)':y='y':d=$3" -c:v libx264 $4
