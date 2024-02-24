# Durdraw Plugin
# Type: Transform Movie
# Name: Bounce |> -> |><|, aka Ping-Pong

import copy

# Durdraw plugin format version
durdraw_plugin_version = 1

# Plugin information
durdraw_plugin = {
    "name": "Bounce",
    "author": "Sam Foster, samfoster@gmail.com",
    "version":  1,   # Plugin verison, if applicable
    "type": "transform_movie",
    "desc": "Duplicate all frames and reverse them, then append them to the end. |> -> |><|"
}

def transform_movie(mov):
    # Make a copy of the frames
    newframes = copy.deepcopy(mov.frames)
    # Remove the last frame, otherwise it will be shown 2 times in a row after transform
    newframes.pop()
    # Reverse copy with slicing trick
    newframes = newframes[::-1]
    # Remove the last frame again, for the same reason (when it loops back around)
    newframes.pop()
    # Append it to the movie frames
    mov.frames = mov.frames + newframes
    mov.frameCount = len(mov.frames)
    return mov
 
