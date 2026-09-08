# Durdraw Plugin
# Type: Transform Movie
# Name: Repeat |> -> |>|>


import copy

# Durdraw plugin format version
durdraw_plugin_version = 1

# Plugin information
durdraw_plugin = {
    'name': 'Repeat',
    'author': 'Sam Foster, samfoster@gmail.com',
    'version':  1,   # Plugin verison, if applicable
    'provides': ['transform_movie'],
    "type": ["effect"],
    'desc': 'Duplicate all frames and append them to the end. |> -> |>|>'
}

opts = {
    'count': 1,
}

def transform_movie(mov, appState=None, opts=opts):
    # Make a copy of the frames
    mov.newframes = copy.deepcopy(mov.frames)
    # Append it to the movie frames
    for i in range(0, opts['count']):
        mov.frames = mov.frames + mov.newframes
    mov.frameCount = len(mov.frames)
    return mov
 
