# Durdraw Plugin
# Type: Transform Movie
# Name: Plasma Overlay

import math

# Durdraw plugin format version
durdraw_plugin_version = 1

# Plugin information
durdraw_plugin = {
    "name": "Plasma Overlay",
    "author": "Grok (with Sam Foster’s blessing)",
    "version": 1,
    "provides": ["transform_movie"],
    "desc": "Overlays a swirling plasma color effect on existing frames."
}

def transform_movie(mov, appState=None):
    """Applies a plasma color effect to existing frames, preserving original characters."""
    # Use existing frame count
    steps = mov.frameCount
    
    # Color setup
    color_mode = appState.colorMode if appState else "16"
    max_color = 255 if color_mode == "256" else 15  # Full palette range
    
    for step in range(steps):
        frame = mov.frames[step]  # Work with existing frame
        time = step / steps * 2 * math.pi  # Phase over movie length
        
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
                # Only update color, keep original char
                frame.newColorMap[y][x] = [fg_color, frame.newColorMap[y][x][1]]  # Preserve bg
        
        # Frame is already in mov.frames—no need to add
    
    return mov

from durdraw.durdraw_movie import Frame  # Adjust import path as needed

