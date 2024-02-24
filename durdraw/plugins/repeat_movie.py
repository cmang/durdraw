# Durdraw Plugin - Transform - Repeat |> -> |>|>

import copy

# Durdraw plugin format version
durdraw_plugin_version = 1

# Plugin information
durdraw_plugin = {
    "name": "Repeat Movie",
    "author": "Sam Foster, samfoster@gmail.com",
    "version":  1,   # Plugin verison, if applicable
    "type": "transform_movie",
    "desc": "Duplicate all frames and append them to the end. |> -> |>|>"
}

def transform_movie(mov):
    # Make a copy of the frames
    mov.newframes = copy.deepcopy(mov.frames)
    # Append it to the movie frames
    mov.frames = mov.frames + mov.newframes
    mov.frameCount = len(mov.frames)
    return mov
 
