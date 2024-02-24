# Durdraw Plugin
# Type: Transform Movie
# Name: Bounce |> -> |><|, aka Ping-Pong

import copy

# Durdraw plugin format version
durdraw_plugin_version = 1

# Plugin information
durdraw_plugin = {
    "name": "Bounce Movie",
    "author": "Sam Foster, samfoster@gmail.com",
    "version":  1,   # Plugin verison, if applicable
    "type": "transform_movie",
    "desc": "Duplicate all frames and reverse them, then append them to the end. |> -> |><|"
}

def transform_movie(mov):
    # Make a copy of the frames
    newframes = copy.deepcopy(mov.frames)
    # Reverse copy with slicing trick
    newframes = newframes[::-1]
    # Append it to the movie frames
    mov.frames = mov.frames + newframes
    mov.frameCount = len(mov.frames)
    return mov
 
