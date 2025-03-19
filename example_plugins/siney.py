# Durdraw Plugin
# Type: Transform Movie
# Name: Sine Wave

import math
from copy import deepcopy
from durdraw.durdraw_movie import Frame  # Adjust import path as needed

# Durdraw plugin format version
durdraw_plugin_version = 1

# Plugin information
durdraw_plugin = {
    "name": "Sine Wave",
    "author": "Grok (with Sam Foster’s blessing)",
    "version": 1,
    "provides": ["transform_movie"],
    "desc": "Oscillates characters horizontally with a sine wave over existing frames."
}

def transform_movie(mov, appState=None):
    """Shifts chars left/right with a sine wave, preserving original content and colors."""
    orig_frames = deepcopy(mov.frames)  # Save original frames
    mov.frames = []  # Clear for new frames
    mov.frameCount = 0
    
    # Animation settings
    amplitude = 5  # Max shift in chars (tweakable)
    period = 20    # Frames for one full wave cycle (tweakable)
    steps = period  # Total frames in the loop
    
    for step in range(steps):
        frame = Frame(mov.sizeX, mov.sizeY)  # New frame
        # Sine phase for this frame
        phase = (step / period) * 2 * math.pi
        
        for y in range(mov.sizeY):
            # Calculate horizontal shift for this row
            shift = int(amplitude * math.sin(phase + (y / mov.sizeY) * 2 * math.pi))
            orig_line = orig_frames[0].content[y]  # Use first frame as base
            orig_colors = orig_frames[0].newColorMap[y]
            
            for x in range(mov.sizeX):
                # Shifted position, wrapping around
                src_x = (x - shift) % mov.sizeX
                frame.content[y][x] = orig_line[src_x]
                frame.newColorMap[y][x] = orig_colors[src_x]
        
        frame.delay = 0.05  # Fast playback for smooth wave (adjustable)
        mov.addFrame(frame)
    
    return mov


