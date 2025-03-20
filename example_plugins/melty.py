# Durdraw Plugin
# Type: Transform Movie
# Name: Melt

import random
from copy import deepcopy
from durdraw.durdraw_movie import Frame

# Durdraw plugin format version
durdraw_plugin_version = 1

# Plugin information
durdraw_plugin = {
    "name": "Melt",
    "author": "Grok (with Sam Foster’s blessing)",
    "version": 1,
    "provides": ["transform_movie"],
    "desc": "Melts filled characters downward into a puddle like dripping oatmeal."
}

def transform_movie(mov, appState=None):
    """Melts filled chars downward unevenly, piling into a puddle over 30 frames."""
    orig_frame = deepcopy(mov.frames[0])  # Frame to melt
    mov.frames = []  # Clear for new frames
    mov.frameCount = 0
    
    # Animation settings
    steps = 30  # Frames for full melt
    
    # Track positions: (x, y) -> (char, color)
    positions = {}  # Current positions of melting chars
    puddle = {}    # Final resting spots at bottom
    
    # Initialize with filled chars only
    for y in range(mov.sizeY):
        for x in range(mov.sizeX):
            if orig_frame.content[y][x] != ' ':  # Only non-blank chars
                positions[(x, y)] = [orig_frame.content[y][x], orig_frame.newColorMap[y][x]]
    
    # Drip speeds per column (water-like variation)
    drip_rates = [random.uniform(0.5, 1.5) for _ in range(mov.sizeX)]  # Faster/slower columns
    
    for step in range(steps):
        frame = Frame(mov.sizeX, mov.sizeY)
        
        # Initialize frame with spaces
        for y in range(mov.sizeY):
            for x in range(mov.sizeX):
                frame.content[y][x] = ' '
                frame.newColorMap[y][x] = [1, 0]  # White fg, black bg
        
        # Move dripping chars
        new_positions = {}
        for (x, y), (char, color) in positions.items():
            # Drip distance based on step and column rate
            drip_dist = int(step * drip_rates[x] / steps * (mov.sizeY - y))
            new_y = min(y + drip_dist, mov.sizeY - 1)  # Don’t exceed bottom
            
            # Simple water sim: stack if blocked, else drip
            while (x, new_y) in new_positions or (x, new_y) in puddle:
                new_y -= 1  # Stack up if spot’s taken
                if new_y <= y:  # Can’t go up past start
                    new_y = y + 1  # Rest just below
                    break
            
            if new_y == mov.sizeY - 1 or (x, new_y + 1) in puddle:  # Hit bottom or puddle
                puddle[(x, new_y)] = [char, color]
            else:
                new_positions[(x, new_y)] = [char, color]
        
        # Update positions for next frame
        positions = new_positions
        
        # Render current dripping chars
        for (x, y), (char, color) in positions.items():
            frame.content[y][x] = char
            frame.newColorMap[y][x] = color
        
        # Render puddle
        for (x, y), (char, color) in puddle.items():
            frame.content[y][x] = char
            frame.newColorMap[y][x] = color
        
        mov.addFrame(frame)
    
    # Final frame: all in puddle
    final_frame = Frame(mov.sizeX, mov.sizeY)
    for y in range(mov.sizeY):
        for x in range(mov.sizeX):
            if (x, y) in puddle:
                final_frame.content[y][x] = puddle[(x, y)][0]
                final_frame.newColorMap[y][x] = puddle[(x, y)][1]
            else:
                final_frame.content[y][x] = ' '
                final_frame.newColorMap[y][x] = [1, 0]
    mov.addFrame(final_frame)
    
    return mov

