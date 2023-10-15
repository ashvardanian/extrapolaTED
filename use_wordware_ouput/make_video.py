#!/usr/bin/env python3
""" make_video.py

    Usage:
        ./make_video.py <my_ted_data>.json

    Output:
       * Downloads associated files into the directory <my_ted_data>_files/
       * Creates <my_ted_data>.mpg, a video file
"""

# ______________________________________________________________________
# Imports

import json
import os
import subprocess
import sys
from inspect import cleandoc
from pathlib import Path


# ______________________________________________________________________
# Main

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    input_path = Path(sys.argv[1])
    basename   = input_path.stem

    with input_path.open() as f:
        data = json.load(f)
    assert type(data) is list

    # Ensure data directory exists.
    data_dir = Path(str(basename) + '_data')
    data_dir.mkdir(exist_ok=True)

    print('Ensuring images and audio are downloaded')
    cd_prefix = f'cd {data_dir.absolute()} &&'
    for block in data:
        # The -nc flag prevents re-downloading; for faster development.
        os.system(f'{cd_prefix} wget -nc {block["audio"]}')
        os.system(f'{cd_prefix} wget -nc {block["image"]}')
    os.system(f'cp silence.mp3 {data_dir.absolute()}')

    # Discover the audio durations of each mp3 file.
    print('Checking time durations of each audio clip')
    ffprobe_cmd = ' '.join(cleandoc('''
        ffprobe -v error -show_entries format=duration -of
        default=noprint_wrappers=1:nokey=1
    ''').split('\n'))
    times = []
    for block in data:
        audio_fname = Path(block['audio']).name
        audio_path = data_dir / audio_fname
        cmd = ffprobe_cmd + ' ' + str(audio_path.absolute())
        result = subprocess.run(cmd.split(), stdout=subprocess.PIPE)
        times.append(float(result.stdout.decode()))
    print(times)

    # Put together a single audio track.
    fnames = []
    fnames.append(f"file 'silence.mp3'")
    for i, block in enumerate(data):
        fnames.append("file '" + Path(block['audio']).name + "'")
        fnames.append(f"file 'silence.mp3'")
    audio_txt = data_dir / 'audio.txt'
    with audio_txt.open('w') as f:
        f.write('\n'.join(fnames) + '\n')
    cmd = 'ffmpeg -f concat -safe 0 -i audio.txt -c copy full_audio.mp3'
    os.system(f'{cd_prefix} {cmd}')

    # Create the video file.
    commands = []
    for i, block in enumerate(data):
        commands.append("file '" + Path(block['image']).name + "'")
        duration = times[i] + 1
        if i == 0 or i == len(data) - 1:
            duration += 0.5
        commands.append(f'duration {duration}')
    images_txt = data_dir / 'images.txt'
    with images_txt.open('w') as f:
        f.write('\n'.join(commands) + '\n')
    cmd = 'ffmpeg -f concat -safe 0 -i images.txt -i full_audio.mp3 -vsync vfr -pix_fmt yuv420p video.mp4'
    os.system(f'{cd_prefix} {cmd}')
