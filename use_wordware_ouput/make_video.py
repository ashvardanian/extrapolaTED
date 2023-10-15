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




