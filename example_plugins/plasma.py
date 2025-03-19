# Durdraw Plugin
# Type: Transform Movie
# Name: Plasma

import math
from copy import deepcopy

# Durdraw plugin format version
durdraw_plugin_version = 1

# Plugin information
durdraw_plugin = {
    "name": "Plasma",
    "author": "Grok (with Sam Foster’s blessing)",
    "version": 1,
    "provides": ["transform_movie"],
    "desc": "Generates a swirling plasma animation with shifting colors."
}

def transform_movie(mov, appState=None):
    """Creates a plasma effect with sine-based color waves across the canvas."""
    mov.frames = []  # Clear for new frames
    mov.frameCount = 0
    
    # Animation settings
    steps = 50  # Frames for a full cycle (smooth loop)
    color_mode = appState.colorMode if appState else "16"  # Default to 16-color
    max_color = 255 if color_mode == "256" else 15  # Color range
    
    for step in range(steps):
        frame = Frame(mov.sizeX, mov.sizeY)  # Fresh frame
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
                fg_color = int(1 + (value + 1) * (max_color - 1) / 2)
                frame.content[y][x] = 'X'  # Static char—color does the work
                frame.newColorMap[y][x] = [fg_color, 0]  # Black bg
        
        mov.addFrame(frame)
    
    return mov

from durdraw.durdraw_movie import Frame  # Adjust import path as needed

