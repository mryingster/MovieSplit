#!/usr/bin/env python
import sys, os, subprocess

def getChapters(filename):
    chapters = []
    command = ["ffprobe", "-i", filename]

    try:
        # ffmpeg requires an output file and so it errors
        # when it does not get one so we need to capture stderr,
        # not stdout.
        output = subprocess.check_output(command,
                                         stderr=subprocess.STDOUT,
                                         universal_newlines=True)
    except subprocess.CalledProcessError, e:
        output = e.output

    for line in iter(output.splitlines()):
        if line.strip().startswith("Chapter"):
            chapters.append({
                "chapter" : len(chapters),
                "start"   : line.split("start")[-1].split(",")[0].strip(),
                "end"     : line.split("end")[-1].strip(),
                "fname"   : filename,
            })

    return chapters

def convertChapters(chapters):
  for chap in chapters:
    print "start:" +  chap['start']
    print chap
    command = [
        "ffmpeg", '-i', chap['fname'],
        '-vcodec', 'copy',
        '-acodec', 'copy',
        '-ss', chap['start'],
        '-to', chap['end'],
        "%s_%s" % (chap["chapter"], chap['fname'])
    ]
    output = ""
    try:
        # ffmpeg requires an output file and so it errors
        # when it does not get one
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError, e:
        output = e.output
        raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

def __main__():
    for file in sys.argv[1:]:
        chapters = getChapters(file)

        # Shaun the Sheep episodes come in groups of three!
        shaun_chapters = []
        for i in range(0, len(chapters), 3):
            shaun_chapters.append({
                "chapter" : len(shaun_chapters),
                "start"   : chapters[i]["start"],
                "end"     : chapters[i+2]["end"],
                "fname"   : chapters[i]["fname"],
            })

        convertChapters(shaun_chapters)
    quit()


__main__()
