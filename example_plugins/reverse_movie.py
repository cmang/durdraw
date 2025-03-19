# Durdraw Plugin
# Type: Transform Movie
# Name: Reverse |> -> <|

# Durdraw plugin format version
durdraw_plugin_version = 1

# Plugin information
durdraw_plugin = {
    "name": "Reverse",
    "author": "Sam Foster, samfoster@gmail.com",
    "version":  1,   # Plugin verison, if applicable
    "provides": ["transform_movie"],
    "desc": "Reverses the order of the frames in a movie"
}

def transform_movie(mov, appState=None):
    # Use slicing trick to reverse frames
    mov.frames = mov.frames[::-1]
    return mov
 
