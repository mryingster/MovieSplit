Movie Split - A Python Script
-----------------------------

This is a simple Python script to run shell commands,`ffprobe` and `ffmpeg`, on a video file, and split it up according to chapter markers. The script will prompt the user to select chapters by which the video file will be split.

Resulting output files will be in the form of [moviename]_chapter_[n].[ext].

Requirements
------------

This requires `ffmpeg` to be installed

Notes
-----

Original code used was taken from this git project:
https://gist.github.com/dcondrey/469e2850e7f88ac198e8c3ff111bda7c
