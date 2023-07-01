#!/opt/homebrew/bin/python3

import os
import sys
import json
import shutil
import re
import subprocess


IGNORED_FILES = [
    'user-generated-memory-titles.json',
    'shared_album_comments.json',
    'print-subscriptions.json',
    'metadata.json'
]

def process_json_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.json') and file not in IGNORED_FILES:
                process_json(root, file, files)

def process_mp_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.mp') and file not in IGNORED_FILES:
                process_mp(root, file)

def apply_meta(directory):
    exiftool_command = [
        'exiftool',
        '-d', '%s',                                  # dateformat is timestamp
        '-tagsfromfile', '%d%f.%e.json',             # use same filename + json to find meta
        '-description',                              # appply description
        '-title',                                    # apply title
        '-DateTimeOriginal<PhotoTakenTimeTimestamp', # apply photoTakenTime.timestamp to DateTimeOriginal
        '-FileCreateDate<PhotoTakenTimeTimestamp',   # apply photoTakenTime.timestamp to FileCreateDate
        '-FileModifyDate<PhotoTakenTimeTimestamp',   # apply photoTakenTime.timestamp to FileModifyDate
        '-gpslatitude<GeoDataLatitude',              # apply geoData.latitude to gpslatitude
        '-gpslatituderef<GeoDataLatitude',           # apply geoData.latitude to gpslatituderef
        '-gpslongitude<GeoDataLongitude',            # apply geoData.longitude to gpslongitude
        '-gpslongituderef<GeoDataLongitude',         # apply geoData.longitude to gpslongitude
        '-overwrite_original',                       # apply in place
        '-r',                                        # recursively
        directory                                    # where to find files
    ]
    subprocess.run(exiftool_command)
    print(f"Metadata applied to {directory}")

def remove_json_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.json'):
                os.remove(os.path.join(root, file))

def process_json(root, file, files):
    json_file_path = os.path.join(root, file)
    filename = file.split('.')[0]
    count = 0

    for target_file in find_target_files(filename, files):
        target_file_path = os.path.join(root, target_file)
        new_json_file_path = target_file_path + '.json'
        if json_file_path != new_json_file_path:
           print(f"Copy {json_file_path} to {new_json_file_path}")
           shutil.copy2(json_file_path, new_json_file_path)
        count += 1

    if count == 0:
        print(f"No matching file found for {filename}, json {json_file_path}")

def process_mp(root, file):
    path = os.path.join(root, file)
    new_path = re.sub('\.mp', '.mp4', path, flags=re.IGNORECASE)
    print(f"Move {path} to {new_path}")
    shutil.move(path, new_path)

def find_target_files(filename, files):
    for file_path in files:
        another_basename = os.path.basename(file_path)
        if another_basename.startswith(filename) and not another_basename.endswith('json'):
            yield file_path

# Check if a directory argument is provided
if len(sys.argv) < 2:
    print("Please provide the directory path as the first argument.")
    sys.exit(1)

# Extract the directory path from the command-line argument
directory_path = sys.argv[1]

# Check if the directory exists
if not os.path.isdir(directory_path):
    print(f"The directory '{directory_path}' does not exist.")
    sys.exit(1)

process_mp_files(directory_path)
process_json_files(directory_path)
apply_meta(directory_path)
remove_json_files(directory_path)

