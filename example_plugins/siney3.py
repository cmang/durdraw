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
    "name": "Sine Wave 3",
    "author": "Grok (with Sam Foster’s blessing)",
    "version": 1,
    "provides": ["transform_movie"],
    "desc": "Oscillates characters horizontally with multiple sine waves, amplitude swelling and fading."
}

def transform_movie(mov, appState=None):
    """Shifts chars left/right with 10 sine wave cycles, amplitude ramps 0.5 to 5 and back."""
    orig_frames = deepcopy(mov.frames)  # Save original frames
    mov.frames = []  # Clear for new frames
    mov.frameCount = 0
    
    # Animation settings
    max_amplitude = 5    # Peak shift in chars
    min_amplitude = 0.5  # Starting subtle shift
    cycles = 10          # Number of oscillation cycles
    steps_per_cycle = 10 # Frames per cycle (smooth wave)
    total_steps = cycles * steps_per_cycle  # Total frames
    
    for step in range(total_steps):
        frame = Frame(mov.sizeX, mov.sizeY)  # New frame
        # Oscillation phase (fast sine for waves)
        phase = (step / steps_per_cycle) * 2 * math.pi
        # Amplitude envelope (slow sine over all steps)
        cycle_progress = step / total_steps  # 0 to 1 over animation
        amplitude = min_amplitude + (max_amplitude - min_amplitude) * math.sin(cycle_progress * math.pi)
        
        for y in range(mov.sizeY):
            # Horizontal shift per row, varying by Y for wave effect
            shift = int(amplitude * math.sin(phase + (y / mov.sizeY) * 2 * math.pi))
            orig_line = orig_frames[0].content[y]  # Base from first frame
            orig_colors = orig_frames[0].newColorMap[y]
            
            for x in range(mov.sizeX):
                # Shifted position, wrapping around
                src_x = (x - shift) % mov.sizeX
                frame.content[y][x] = orig_line[src_x]
                frame.newColorMap[y][x] = orig_colors[src_x]
        
        mov.addFrame(frame)  # Artist controls delay
    
    return mov

