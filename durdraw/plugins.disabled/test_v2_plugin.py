# Durdraw Plugin

import pdb

# Durdraw plugin format version
durdraw_plugin_version = 2

# Plugin information
durdraw_plugin = {
    "name": "Plugin API V2 Test",
    "author": "Sam Foster, samfoster@gmail.com",
    "version":  1,   # Plugin verison, if applicable
    "provides": ["transform_movie"],
    "type": ["effect"],
    "desc": "Tests Plugin API Version 2"
}

opts = {
}

# old format:
# def transform_movie(mov, appState=None):
def transform_movie(dur, opts, mov):
    c = dur.color_picker(message="Pick a color for the effect")
    dur.notify(f"Color picked: {c}")
    pl_range = dur.playback_range()
    col_mode = dur.color_mode()
    dur.suspend_ui()
    print('')
    print("Suspended Durdraw UI (curses).")
    print(f"Color picked: {c}")
    print(f"Range: {pl_range}, Color mode: {col_mode}")
    lines = mov.sizeY
    cols = mov.sizeX
    print(f"Canvas lines: {lines}, columns: {cols}")
    print("Press enter to return to Durdraw.")
    input()
    dur.resume_ui()
    return mov

 
