# Durdraw Plugin
# Type: Transform Movie
# Name: Plasma

import math
from copy import deepcopy
from durdraw.durdraw_movie import Frame  # Adjust import path as needed
import pdb

# Durdraw plugin format version
durdraw_plugin_version = 1

# Plugin information
durdraw_plugin = {
    "name": "Plasma",
    "author": "",
    "version": 1,
    "provides": ["transform_movie"],
    "type": ["effect"],
    "desc": "Generates a swirling plasma animation with shifting colors."
}

opts = {
    # Animation settings
    "min color": 1,
    "max color": 255,
    "fill character": ':',
    "overwrite characters": False,
}

def transform_movie(mov, appState=None, opts=opts):
    """Creates a plasma effect with sine-based color waves across the canvas."""
    
    # Animation settings
    low_frame = appState.playbackRange[0] - 1
    high_frame = appState.playbackRange[1]
    steps = high_frame - low_frame
    frame_num = low_frame   # start low

    color_mode = appState.colorMode if appState else "16"  # Default to 16-color
    max_color = opts['max color'] if color_mode == "256" else 15  # Color range
    min_color = opts['min color']
    #min_color = 1
    
    for step in range(steps):
        #frame = Frame(mov.sizeX, mov.sizeY)  # Fresh frame
        frame = mov.frames[frame_num]
        time = step / steps * 2 * math.pi  # Animation phase
        
        for y in range(mov.sizeY):
            for x in range(mov.sizeX):
                # Plasma effect: combine sine waves
                value = (
                    math.sin(x * 0.1 + time) +              # Horizontal wave
                    math.sin(y * 0.1 + time * 1.5) +       # Vertical wave
                    math.sin((x + y) * 0.05 + time * 0.5)  # Diagonal wave
                ) / 3.0  # Average for smooth gradient
                
                # Map to color range (1 to max_color)
                fg_color = int(min_color + (value + 1) * (max_color - 1) / 2)
                if opts['overwrite characters']:
                    frame.content[y][x] = opts['fill character'][0]  # Static char—color does the work
                    frame.newColorMap[y][x] = [fg_color, 0]  # Black bg
                else:
                    if frame.content[y][x] == ' ':
                        frame.content[y][x] = opts['fill character'][0]  # Static char—color does the work
                        frame.newColorMap[y][x] = [fg_color, 0]  # Black bg
        frame_num += 1
    return mov


