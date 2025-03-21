# Durdraw Plugin
# Type: Transform Movie
# Name: Fire

import random
from copy import deepcopy
from durdraw.durdraw_movie import Frame

# Durdraw plugin format version
durdraw_plugin_version = 1

# Plugin information
durdraw_plugin = {
    "name": "Fire Behind 2",
    "author": "Grok (inspired by Asciimatics & Sam Foster)",
    "version": 1,
    "provides": ["transform_movie"],
    "desc": "Renders bonfire-like effects surrounding non-space chars, with originals on top."
}

# Color palette (256-mode, dark grey to yellow)
_COLOURS_256 = [232, 52, 88, 124, 160, 196, 202, 208, 214, 220, 226]  # 232 = dark grey

def transform_movie(mov, appState=None):
    """Renders bonfire-like effects surrounding non-space chars, originals on top."""
    if not mov or not hasattr(mov, 'frames'):  # Safety check
        return mov
    
    current_idx = max(0, mov.currentFrameNumber - 1)  # Clamp to 0
    orig_frame = deepcopy(mov.frames[current_idx])  # Frame to base fire on
    new_frames = []  # Frames to insert
    
    # Animation settings
    steps = 30
    intensity = 0.7  # More frequent for bonfire
    spot_heat = 16   # Higher heat for taller flames
    colour_mode = appState.colorMode if appState else "16"
    colours = _COLOURS_256 if colour_mode == "256" else [8, 1, 9]  # Dark grey, red, yellow
    
    # Heat buffer (taller to allow rise)
    buffer = [[0 for _ in range(mov.sizeX)] for _ in range(mov.sizeY + 3)]  # +3 for flame tips
    
    # Initial heat around objects
    for y in range(mov.sizeY):
        for x in range(mov.sizeX):
            if orig_frame.content[y][x] != ' ':
                if y < mov.sizeY - 1:
                    buffer[y + 1][x] = spot_heat
                if y > 0:
                    buffer[y - 1][x] = spot_heat // 2
                if x > 0:
                    buffer[y][x - 1] = spot_heat // 2
                if x < mov.sizeX - 1:
                    buffer[y][x + 1] = spot_heat // 2
                if y < mov.sizeY - 1 and x > 0:
                    buffer[y + 1][x - 1] = spot_heat // 3
                if y < mov.sizeY - 1 and x < mov.sizeX - 1:
                    buffer[y + 1][x + 1] = spot_heat // 3
                if y > 0 and x > 0:
                    buffer[y - 1][x - 1] = spot_heat // 3
                if y > 0 and x < mov.sizeX - 1:
                    buffer[y - 1][x + 1] = spot_heat // 3
    
    for step in range(steps):
        frame = Frame(mov.sizeX, mov.sizeY)
        for y in range(mov.sizeY):
            for x in range(mov.sizeX):
                frame.content[y][x] = ' '
                frame.newColorMap[y][x] = [232 if colour_mode == "256" else 8, 0]  # Dark grey
        
        # Reseed heat
        for y in range(mov.sizeY):
            for x in range(mov.sizeX):
                if orig_frame.content[y][x] != ' ' and random.random() < intensity:
                    if y < mov.sizeY - 1:
                        buffer[y + 1][x] = random.randint(spot_heat // 2, spot_heat)
                    if y > 0:
                        buffer[y - 1][x] = random.randint(0, spot_heat // 2)
                    if x > 0:
                        buffer[y][x - 1] = random.randint(0, spot_heat // 2)
                    if x < mov.sizeX - 1:
                        buffer[y][x + 1] = random.randint(0, spot_heat // 2)
                    if y < mov.sizeY - 1 and x > 0:
                        buffer[y + 1][x - 1] = random.randint(0, spot_heat // 3)
                    if y < mov.sizeY - 1 and x < mov.sizeX - 1:
                        buffer[y + 1][x + 1] = random.randint(0, spot_heat // 3)
                    if y > 0 and x > 0:
                        buffer[y - 1][x - 1] = random.randint(0, spot_heat // 3)
                    if y > 0 and x < mov.sizeX - 1:
                        buffer[y - 1][x + 1] = random.randint(0, spot_heat // 3)
        
        # Convection (limited rise)
        for y in range(mov.sizeY - 1):  # Only visible range shifts
            if random.random() < 0.7:  # 70% chance for bonfire flicker
                buffer[y] = [buffer[y + 1][x] if buffer[y + 1][x] > buffer[y][x] else buffer[y][x]
                             for x in range(mov.sizeX)]
        
        # Cooling
        for y in range(mov.sizeY + 3):  # Full buffer
            new_row = buffer[y].copy()
            for x in range(mov.sizeX):
                new_val = buffer[y][x]
                count = 1
                if y < mov.sizeY + 2:
                    new_val += buffer[y + 1][x]
                    count += 1
                if y > 0:
                    new_val += buffer[y - 1][x]
                    count += 1
                if x > 0:
                    new_val += buffer[y][x - 1]
                    count += 1
                if x < mov.sizeX - 1:
                    new_val += buffer[y][x + 1]
                    count += 1
                new_row[x] = max(0, new_val // count)
            buffer[y] = new_row
        
        # Render flames
        max_heat = max(max(row) for row in buffer) or 1
        for y in range(mov.sizeY):  # Only visible canvas
            for x in range(mov.sizeX):
                heat = buffer[y][x]
                if heat > 0:
                    colour_idx = min(len(colours) - 1, (heat * len(colours)) // max_heat)
                    frame.content[y][x] = '█'
                    frame.newColorMap[y][x] = [colours[colour_idx], 0]
        
        # Overlay original object
        for y in range(mov.sizeY):
            for x in range(mov.sizeX):
                if orig_frame.content[y][x] != ' ':
                    frame.content[y][x] = orig_frame.content[y][x]
                    frame.newColorMap[y][x] = orig_frame.newColorMap[y][x]
        
        new_frames.append(frame)
    
    # Replace current frame
    mov.frames = mov.frames[:current_idx] + new_frames + mov.frames[current_idx + 1:]
    mov.frameCount = len(mov.frames)
    
    return mov
