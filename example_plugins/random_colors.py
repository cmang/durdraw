# Durdraw Plugin
# Type: Transform Movie
# Name: Random colors

import random
import string

# Durdraw plugin format version
durdraw_plugin_version = 1

# Plugin information
durdraw_plugin = {
    "name": "random colors",
    "author": "Sam Foster, samfoster@gmail.com",
    "version":  1,   # Plugin verison, if applicable
    "provides": ["transform_frame", "transform_movie"],
    "desc": "Fill canvas with random colors."
}

def transform_movie(mov, appState=None):
    frame_num = 0
    for frame in mov.frames:
        mov.frames[frame_num] = transform_frame(frame, appState=appState)
        frame_num += 1
    return mov

def transform_frame(frame, appState=None):
    # fill canvas with random colors.
    if appState.colorMode == "256":
        min_color = 1
        max_color = 255
        bg_color = 0
    else:
        min_color = 1
        max_color = 15
        bg_color = 0
    line_num = 0
    #for line in frame.content:
    while line_num < frame.sizeY:
        col_num  = 0
        #for col in line:
        while col_num < frame.sizeX:
            # Fg colr
            frame.newColorMap[line_num][col_num][0] = random.randrange(min_color, max_color + 1)
            # Bg colr
            frame.newColorMap[line_num][col_num][1] = 0
            col_num += 1
        line_num += 1
    return frame
