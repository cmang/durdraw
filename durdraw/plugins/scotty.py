# Durdraw Plugin
# Type: Transform Movie
# Name: Transporter Fade

import random
from copy import deepcopy

from durdraw.durdraw_movie import Frame  # Adjust import path as needed

# Durdraw plugin format version
durdraw_plugin_version = 1

# Plugin information
durdraw_plugin = {
    "name": "Beam Me Up",
    "author": "",
    "version": 1,
    "provides": ["transform_movie"],
    "type": ["effect"],
    "desc": "Fades in the current frame like a Star Trek transporter with sparkly colors."
}

opts = {
    "steps": 10,
    #"overwrite existing frames": False,
}

def transform_movie(mov, appState=None):
    """Fades in the first frame pixel-by-pixel with sparkly transporter effects."""
    target_frame = deepcopy(mov.currentFrame)  # Frame to fade in
    
    # Animation settings
    steps = opts['steps']  # Frames for fade-in
    #overwrite = opts['overwrite existing frames']
    firstFrameNum = mov.currentFrameNumber
    total_pixels = mov.sizeX * mov.sizeY  # Total spots to fill
    pixels_per_frame = max(total_pixels // steps, 1)  # Fill rate
    
    # Color setup
    color_mode = appState.colorMode if appState else "16"
    if color_mode == "256":
        sparkle_colors = [226, 220, 214, 208]  # Yellow to orange sparkles
        neutral_color = 1  # White for empty
    else:
        sparkle_colors = [13, 12]  # Yellow, bright red
        neutral_color = 7  # Grey
   
    # Start with empty frame
    current_frame = Frame(mov.sizeX, mov.sizeY)
    for y in range(mov.sizeY):
        for x in range(mov.sizeX):
            current_frame.content[y][x] = ' '
            current_frame.newColorMap[y][x] = [neutral_color, 0]
    
    # Track filled positions
    filled = set()
    sparkle_states = {}  # (x, y): sparkle step
    
    for step in range(steps):
        frame = deepcopy(current_frame)  # Build from last frame
        
        # Add new pixels this step
        remaining = total_pixels - len(filled)
        new_pixels = min(pixels_per_frame, remaining)
        for _ in range(new_pixels):
            while True:
                x = random.randint(0, mov.sizeX - 1)
                y = random.randint(0, mov.sizeY - 1)
                pos = (x, y)
                if pos not in filled:
                    break
            filled.add(pos)
            # Start with sparkle
            sparkle_states[pos] = 0  # 0-2: sparkle, 3: final char
        
        # Update sparkles and finalize pixels
        for pos in list(sparkle_states.keys()):
            x, y = pos
            sparkle_step = sparkle_states[pos]
            if sparkle_step < 3:  # Sparkle phase
                if target_frame.content[y][x] != ' ':
                    frame.content[y][x] = random.choice(['.', '*', '+'])  # Sparkly chars
                frame.newColorMap[y][x] = [sparkle_colors[sparkle_step % len(sparkle_colors)], 0]
                sparkle_states[pos] += 1
            else:  # Finalize with target char and color
                frame.content[y][x] = target_frame.content[y][x]
                frame.newColorMap[y][x] = target_frame.newColorMap[y][x]
                del sparkle_states[pos]  # Done sparkling
        
        mov.insertFrame(frame)
        mov.nextFrame()
        current_frame = frame
    
    # Ensure final frame is exact target
    mov.insertFrame(target_frame)
    mov.nextFrame()
    mov.gotoFrame(firstFrameNum)
    mov.deleteCurrentFrame()
    
    return mov


