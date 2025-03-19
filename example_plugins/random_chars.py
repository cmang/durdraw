# Durdraw Plugin
# Type: Transform Movie
# Name: Random Letters

import random
import string

# Durdraw plugin format version
durdraw_plugin_version = 1

# Plugin information
durdraw_plugin = {
    "name": "random letters",
    "author": "Sam Foster, samfoster@gmail.com",
    "version":  1,   # Plugin verison, if applicable
    "provides": ["transform_frame", "transform_movie"],
    "desc": "Fill canvas with random letters."
}

def transform_movie(mov, appState=None):
    frame_num = 0
    for frame in mov.frames:
        mov.frames[frame_num] = transform_frame(frame, appState=appState)
        frame_num += 1
    return mov

def transform_frame(frame,appState=None):
    # fill canvas with random letters.
    line_num = 0
    while line_num < frame.sizeY:
        col_num  = 0
        #for col in line:
        while col_num < frame.sizeX:
            frame.content[line_num][col_num] = random.choice(string.ascii_letters)
            col_num += 1
        line_num += 1
    return frame
