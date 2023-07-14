#!/bin/bash
export PYTHONPATH+=$(pwd)
blender  --background --python piece_rendering.py
ffmpeg -y -framerate 4 -pattern_type glob -i 'puzzle_state*.png' -vf reverse -c:v libx264 -pix_fmt yuv420p mount_puzzle.mp4
ffmpeg -y -framerate 4 -pattern_type glob -i 'puzzle_state*.png' -c:v libx264 -pix_fmt yuv420p dismount_puzzle.mp4
