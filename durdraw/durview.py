# Durview. Part of Durdraw - https://github.com/cmang/durdraw
# main() entry point

import argparse
import configparser
import curses
import os
import sys
import time
import pathlib

from durdraw import log
from durdraw.durdraw_appstate import AppState
from durdraw.durdraw_ui_curses import UserInterface as UI_Curses
from durdraw.durdraw_options import Options
import durdraw.help

@log.log_on_crash
def main(fetch_args=None):
    DURVIEW_VER = "0.1.0"
    DUR_FILE_VER = 7

    # Get command-line arguments
    parser = argparse.ArgumentParser()
    parserColorModeMutex = parser.add_mutually_exclusive_group()
    #parserFilenameMutex.add_argument("filename", nargs='?', help=".dur or ascii file to load")
    #parserFilenameMutex.add_argument("-p", "--play", help="Just play .dur, .ANS or .ASC file or files, then exit",
                    #nargs='+')
    parser.add_argument("filename", help=".ANS, .ASC or .dur file(s) to view", nargs='*')
    parserColorModeMutex.add_argument("--256color", help="Try 256 color mode", action="store_true", dest='hicolor')
    parserColorModeMutex.add_argument("--16color", help="Try 16 color mode", action="store_true", dest='locolor')
    parser.add_argument("--cp437", help="Display extended characters on the screen using Code Page 437 (IBM-PC/MS-DOS) encoding instead of Utf-8. (Requires CP437 capable terminal and font) (beta)", action="store_true")
    parser.add_argument("-b", "--blackbg", help="Use a black background color instead of terminal default", action="store_true")
    parser.add_argument("--wrap", help="Number of columns to wrap lines at when loading ASCII and ANSI files (default 80)", nargs=1, type=int)
    parser.add_argument("--nomouse", help="Disable mouse support",
                    action="store_true")
    parser.add_argument("--theme", help="Load a custom theme file", nargs=1)
    parser.add_argument("-V", "--version", help="Show version number and exit",
                    action="store_true")
    parser.add_argument("--debug", action="store_true", help=argparse.SUPPRESS)
            
    args = parser.parse_args(fetch_args)

    if args.version:
        print(DURVIEW_VER)
        exit(0)

    # Initialize application
    app = AppState()    # to store run-time preferences from CLI, environment stuff, etc.
    app.setDurVer(DURVIEW_VER)
    app.setDurFileVer(DUR_FILE_VER)
    app.showStartupScreen=False
    app.quickStart = True
    app.durview_running = True
    if app.sixteenc_available:
        # Start in 16c mode by default, for now
        app.sixteenc_browsing = True

    # Parse general command-line paramaters
    if args.debug:
        app.setDebug(True)
    if args.wrap:
        app.wrapWidth = args.wrap[0]
    if args.nomouse:
        app.hasMouse = False
    if args.hicolor:
        app.colorMode = "256"
    if args.locolor:
        app.colorMode = "16"
    if args.cp437:
        app.charEncoding = 'cp437'

    if args.blackbg:
        app.blackbg = False
    else:
        app.blackbg = True

    # load configuration file
    if app.loadConfigFile():
        # Load main optiona
        if 'Main' in app.configFile:
            mainConfig = app.configFile['Main']
            # load color mode 
            if 'color-mode' in mainConfig:
                app.colorMode = mainConfig['color-mode']
            if 'disable-mouse' in mainConfig:
                if mainConfig.getboolean('disable-mouse'):
                    app.hasMouse = False
        # load theme set in config fileFalse
        if app.colorMode == "256":
            app.loadThemeFromConfig("Theme-256")
        else:
            app.loadThemeFromConfig("Theme-16")
    if args.theme:
        if app.colorMode == "256":
            app.loadThemeFile(args.theme[0], "Theme-256")
        else:
            app.loadThemeFile(args.theme[0], "Theme-16")
        app.customThemeFile = args.theme[0]


    # Load help file - first look for resource path, eg: python module dir
    durhelp_fullpath = ''
    durhelp256_fullpath = pathlib.Path(__file__).parent.joinpath("help/durhelp-256-long.dur")
    durhelp16_fullpath = pathlib.Path(__file__).parent.joinpath("help/durhelp-16-long.dur")
    app.durhelp256_fullpath = durhelp256_fullpath
    app.durhelp16_fullpath = durhelp16_fullpath

    if args.filename:
        app.playOnlyMode = True
        app.editorRunning = False

    # Initialize UI/Durdraw object (durdraw_ui_curses.py)
    ui = UI_Curses(app)

    if app.hasMouse:
        ui.initMouse()
    if app.blackbg:
        ui.enableTransBackground()
    if args.filename:
        if os.path.isdir(args.filename[0]):
            # If the first paramater is a directory, treat that as the starting folder.
            app.workingLoadDirectory = args.filename[0]
            app.sixteenc_browsing = False
        else:   # Otherwise, add all the files to the play queue.
            app.play_queue = args.filename
    while app.durview_running:
        ui.runDurView()
    ui.verySafeQuit()

if __name__ == "__main__":
    main()


