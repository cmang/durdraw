#!/usr/bin/env python3

import curses, os, subprocess

# Durdraw plugin format version
durdraw_plugin_version = 2

# Plugin information
durdraw_plugin = {
    "name": "Jump to Shell",    # Item as it apperas in the menu
    "author": "",
    "version": 1,
    "provides": ["transform_movie"],
    "desc": "Jump out to the shell, similar to Jump to DOS in TheDraw",
    # Menu stuff
    "type": "menu_item",
    "shortcut": "j",       # Keyboard shurtcut when menu is open   
    "location": "Menu"     # Menu for submenu to go in
}

# Plugin options
opts = {
}

def transform_movie(dur, opts, mov):
    dur.suspend_ui()
    shell = os.getenv("SHELL")
    print("Type 'exit' to return to durdraw.")
    subprocess.run(shell)
    input('Press enter to return to Durdraw...')
    dur.resume_ui()
    return mov

