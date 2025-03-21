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
    "name": "Fire - Pink Flames",
    "author": "Grok (inspired by Asciimatics & Sam Foster)",
    "version": 1,
    "provides": ["transform_movie"],
    "desc": "Renders steady fire effects over non-space chars"
}

_COLOURS_256 = [235, 53, 89, 125, 161, 197, 203, 204, 205, 206, 212]  # Dark grey to hot pink

def transform_movie(mov, appState=None):
    """Renders steady fire effects under/around non-space chars, replacing frame for looping."""
    current_idx = mov.currentFrameNumber - 1  # 1-based UI to 0-based index
    orig_frame = deepcopy(mov.frames[current_idx])  # Frame to base fire on
    new_frames = []  # Frames to insert
    
    # Animation settings
    steps = 30
    intensity = 0.6
    spot_heat = 16  # Tiny, steady flames
    colour_mode = appState.colorMode if appState else "16"
    colours = _COLOURS_256 if colour_mode == "256" else [0, 1, 9]
    
    # Heat buffer
    buffer = [[0 for _ in range(mov.sizeX)] for _ in range(mov.sizeY + 2)]
    
    # Initial heat under/around objects
    for y in range(mov.sizeY):
        for x in range(mov.sizeX):
            if orig_frame.content[y][x] != ' ':
                if y < mov.sizeY - 1:
                    buffer[y + 1][x] = spot_heat
                if x > 0:
                    buffer[y][x - 1] = spot_heat // 2
                if x < mov.sizeX - 1:
                    buffer[y][x + 1] = spot_heat // 2
    
    for step in range(steps):
        frame = Frame(mov.sizeX, mov.sizeY)
        for y in range(mov.sizeY):
            for x in range(mov.sizeX):
                frame.content[y][x] = ' '
                frame.newColorMap[y][x] = [0, 0]
        
        # Reseed heat steadily (no rising)
        for y in range(mov.sizeY):
            for x in range(mov.sizeX):
                if orig_frame.content[y][x] != ' ' and random.random() < intensity:
                    if y < mov.sizeY - 1:
                        buffer[y + 1][x] = random.randint(spot_heat // 2, spot_heat)
                    if x > 0:
                        buffer[y][x - 1] = random.randint(0, spot_heat // 2)
                    if x < mov.sizeX - 1:
                        buffer[y][x + 1] = random.randint(0, spot_heat // 2)
        
        # Cooling (no convection)
        for y in range(mov.sizeY):
            new_row = buffer[y].copy()
            for x in range(mov.sizeX):
                new_val = buffer[y][x]
                count = 1
                if y < mov.sizeY - 1:
                    new_val += buffer[y + 1][x]
                    count += 1
                if x > 0:
                    new_val += buffer[y][x - 1]
                    count += 1
                if x < mov.sizeX - 1:
                    new_val += buffer[y][x + 1]
                    count += 1
                new_row[x] = max(0, new_val // count)
            buffer[y] = new_row
        
        # Render flames (no original chars)
        max_heat = max(max(row) for row in buffer) or 1
        for y in range(mov.sizeY):
            for x in range(mov.sizeX):
                heat = buffer[y][x]
                if heat > 0:
                    colour_idx = min(len(colours) - 1, (heat * len(colours)) // max_heat)
                    frame.content[y][x] = '█'
                    frame.newColorMap[y][x] = [colours[colour_idx], 0]
        
        new_frames.append(frame)
    
    # Replace current frame with fire frames for smooth loop
    mov.frames = mov.frames[:current_idx] + new_frames + mov.frames[current_idx + 1:]
    mov.frameCount = len(mov.frames)
    
    return mov
