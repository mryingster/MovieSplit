#!/usr/bin/env python
import sys, os, subprocess

def getDuration(s, e):
    d = float(e) - float(s)
    hours     = int(d / (60 * 60))
    minutes   = int(d / 60 % 60)
    seconds   = int(d % 60)
    remainder = int(d * 1000) % 1000
    return "%02d:%02d:%02d.%03d" % (hours, minutes, seconds, remainder)

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
            start    = line.split("start")[-1].split(",")[0].strip()
            end      = line.split("end")[-1].strip()
            duration = getDuration(start, end)
            chapters.append({
                "chapter"  : len(chapters),
                "start"    : start,
                "end"      : end,
                "fname"    : filename,
                "duration" : duration,
            })

    return chapters

def convertChapters(chapters):
    for chapter in chapters:
        extension = chapter['fname'].split('.', 1)[-1]
        base_name = chapter['fname'].split('.', 1)[0]
        new_name  = "%s_chapter_%s.%s" %(base_name, chapter["chapter"], extension)

        print("Writing file, %s \n(Start: %s End: %s Duration: %s)" % (
            new_name,
            chapter['start'],
            chapter['end'],
            chapter['duration'],
        ))

        command = [
            "ffmpeg", '-i', chapter['fname'],
            '-vcodec', 'copy',
            '-acodec', 'copy',
            '-ss', chapter['start'],
            '-to', chapter['end'],
            new_name,
        ]
        output = ""
        try:
            # ffmpeg requires an output file and so it errors
            # when it does not get one
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
        except subprocess.CalledProcessError, e:
            output = e.output
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    return

def selectChapters(chapters):
    selected = []
    while 1:
        print("Chapters Found:")
        for i in range(len(chapters)):
            print(" [%s]  %2s) %-16s %-16s %s" % (
                "x" if i in selected else " ",
                i,
                chapters[i]["duration"],
                chapters[i]["start"],
                chapters[i]["end"],
            ))

        print("")
        print("Select chapters to split on. Press enter to proceed.")
        selection = raw_input("Selection: ")
        print selection
        if selection.lower() in ["q", "x"]:
            quit()
        if selection == "":
            break
        if selection.lower() == "a":
            selected = [i for i in range(len(chapters))]
        if selection.lower() in ["c", "n"]:
            selected = []
        if selection.isdigit():
            if int(selection) >= 0 and int(selection) < len(chapters):
                if int(selection) in selected:
                    selected.pop(selected.index(int(selection)))
                else:
                    selected.append(int(selection))
                    selected = sorted(selected)
            else:
                print("Invalid selection!")

    # Create new list of selected chapters
    new_chapters = []
    for i in range(len(selected)):
        chapter_index = selected[i]

        # Determine where next split occurs
        # If there are no more designated splits, go to end of last chapter
        next_chapter = None
        if i == len(selected) - 1:
            next_chapter = len(chapters) - 1
        else:
            next_chapter = selected[i+1] - 1

        start    = chapters[chapter_index]["start"]
        end      = chapters[next_chapter]["end"]
        duration = getDuration(start, end)
        new_chapters.append({
            "chapter"  : chapters[chapter_index]["chapter"],
            "start"    : start,
            "end"      : end,
            "fname"    : chapters[chapter_index]["fname"],
            "duration" : duration,

        })
    return new_chapters

def __main__():
    for file in sys.argv[1:]:
        chapters_in = getChapters(file)

        chapters_out = selectChapters(chapters_in)

        convertChapters(chapters_out)
    quit()


__main__()
