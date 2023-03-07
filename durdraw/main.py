# Part of Durdraw - https://github.com/cmang/durdraw
# main() entry point

import argparse
import os
import sys
import time
import pathlib

from durdraw.durdraw_appstate import AppState
from durdraw.durdraw_ui_curses import UserInterface as UI_Curses
from durdraw.durdraw_options import Options
import durdraw.help

class ArgumentChecker:
    """ Place to hold any methods for verifying CLI arguments, beyond
        what argparse can do on its own. Call these methods via
        argparse.add_argument(.. type= ..) paramaters. """
    def undosize(size_s):
        size = int(size_s)  # because it comes as a string
        if size >= 1 and size <= 1000:
            return size
        else:
            raise argparse.ArgumentTypeError("Undo size must be between 1 and 1000.")

def main():
    DUR_VER = '0.18.2'
    DUR_FILE_VER = 5
    DEBUG_MODE = False # debug = makes debug_write available, sends more notifications
    durlogo = '''
       __                __
     _|  |__ __ _____ __|  |_____ _____ __ __ __
    / _  |  |  |   __|  _  |   __|  _  |  |  |  |\\
   /_____|_____|__|__|_____|__|___\____|________| |  Durr....
   \_____________________________________________\|  v %s
    Press esc-h for help.
    ''' % DUR_VER
    argChecker = ArgumentChecker()
    parser = argparse.ArgumentParser()
    parserStartScreenMutex = parser.add_mutually_exclusive_group()
    parserFilenameMutex = parser.add_mutually_exclusive_group()
    parserColorModeMutex = parser.add_mutually_exclusive_group()
    parserFilenameMutex.add_argument("filename", nargs='?', help=".dur or ascii file to load")
    parserFilenameMutex.add_argument("-p", "--play", help="Just play .dur file or files, then exit",
                    nargs='+')
    parserStartScreenMutex.add_argument("-q", "--quick", help="Skip startup screen",
                    action="store_true")
    parserStartScreenMutex.add_argument("-w", "--wait", help="Pause at startup screen",
                    action="store_true")
    parserStartScreenMutex.add_argument("-x", "--times", help="Play X number of times (requires -p)",
                    nargs=1, type=int)
    parserColorModeMutex.add_argument("--256color", help="Try 256 color mode", action="store_true", dest='hicolor')
    parserColorModeMutex.add_argument("--16color", help="Try 16 color mode", action="store_true", dest='locolor')
    parser.add_argument("-b", "--blackbg", help="Use a black background color instead of terminal default", action="store_true")
    parser.add_argument("-W", "--width", help="Set canvas width", nargs=1, type=int)
    parser.add_argument("-H", "--height", help="Set canvas height", nargs=1, type=int)
    parser.add_argument("-m", "--max", help="Maximum canvas size for terminal (overrides -W and -H)", action="store_true")
    parser.add_argument("--nomouse", help="Disable mouse support",
                    action="store_true")
    parser.add_argument("-A", "--ansi", help="IBM-PC ANSI Art Mode - Use F1-F10 keys for Code Page 437 extended ASCII (IBM-PC) block characters", action="store_true")
    parser.add_argument("-u", "--undosize", help="Set the number of undo history states - default is 100. More requires more RAM, less saves RAM.", nargs=1, type=int)
    parser.add_argument("-V", "--version", help="Show version number and exit",
                    action="store_true")
    parser.add_argument("--debug", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.version:
        print(DUR_VER)
        exit(0)
    if args.times and not args.play:
        print("-x option requires -p")
        exit(1)
    app = AppState()    # to store run-time preferences from CLI, environment stuff, etc.
    app.setDurVer(DUR_VER)
    app.setDurFileVer(DUR_FILE_VER)
    app.setDebug(DEBUG_MODE)
    if args.debug:
        app.setDebug(True)
    if args.undosize:
        app.undoHistorySize = int(args.undosize[0])
    showStartupScreen=True
    term_size = os.get_terminal_size()
    #if args.width and args.width[0] > 80 and args.width[0] < term_size[0]:
    if args.width and args.width[0] > 1 and args.width[0] < term_size[0]:
        app.width = args.width[0]
    else:
        app.width = 80      # "sane" default screen size, 80x24..
    #if args.height and args.height[0] > 24 and args.height[0] < term_size[1]:
    if args.height and args.height[0] > 1 and args.height[0] < term_size[1]:
        app.height = args.height[0]
    else:
        app.height = 24 - 1
    if args.max:
        if term_size[0] > 80:
           app.width = term_size[0]
        if term_size[1] > 24:
            app.height = term_size[1] - 2
    if args.play:
        showStartupScreen=False
    elif args.quick:
        showStartupScreen=False
    if args.nomouse:
        app.hasMouse = False
    if args.hicolor:
        app.colorMode = "256"
    if args.locolor:
        app.colorMode = "16"
    if args.ansi:
        app.ansiArtMode = True
        app.charEncoding = 'ibm-pc'
    else:
        app.ansiArtMode = False
        app.charEncoding = 'utf-8'
    durhelp_fullpath = pathlib.Path(__file__).parent.joinpath("help/durhelp.dur")
    if args.blackbg:
        app.blackbg = False
    else: app.blackbg = True

    # Load help file - first look for resource path, eg: python module dir
    durhelp_fullpath = ''
    #with importlib.resources.path("durdraw.help", "durhelp.dur") as durhelp_fullpath:
    durhelp_fullpath = pathlib.Path(__file__).parent.joinpath("help/durhelp.dur")
    durhelp256_fullpath = pathlib.Path(__file__).parent.joinpath("help/durhelp-256.dur")
    app.durhelp256_fullpath = durhelp256_fullpath
    #print(f"DEBUG: durhelp_fullpath = {durhelp_fullpath}")
    #print(importlib.resources.path("durdraw.help", "durhelp.dur"))
    #durhelp_fullpath = importlib.resources.path("durdraw.help", "durhelp.dur")
    app.loadHelpFile(durhelp_fullpath)
    if not app.hasHelpFile:
        durhelp_fullpath = 'durdraw/help/durhelp.dur'
        app.loadHelpFile(durhelp_fullpath)

    if showStartupScreen:
        print(durlogo)
        if app.hasHelpFile:
            print(f"Help file: Found in {durhelp_fullpath}")
        else:
            print("Help file: Not found")
        if app.ansiLove:
            print("ansilove = Found")
        else:
            print("ansilove = Not found (no PNG or GIF export support)")
        if app.PIL:
            print("PIL = Found")
        else:
            print("PIL = Not found (no GIF support)")
        if app.hasMouse:
            print("Mouse = Enabled")
        else:
            print("Mouse = Disabled")

        print("Undo history size = %d" % app.undoHistorySize)
        if app.width == 80 and app.height == 24:
            print("Canvas size: %i columns, %i lines (Default)" % (app.width, app.height))
        else:
            print("Canvas size: %i columns, %i lines" % (app.width, app.height))
        if args.wait:
            try:
                choice = input("Press Enter to Continue...")
            except KeyboardInterrupt:
                print("\nCaught interrupt, exiting.")
                exit(0)
        else:
            time.sleep(3)
    if args.play:
        app.playOnlyMode = True
    ui = UI_Curses(app)
    if app.hasMouse:
        ui.initMouse()
    if app.blackbg:
        ui.enableTransBackground()
    if args.filename:
        ui.loadFromFile(args.filename, 'dur')
    if args.play:
        # Just play files and exit
        app.drawBorders = False
        if args.times:
            app.playNumberOfTimes = args.times[0]
        for movie in args.play:
            ui.loadFromFile(movie, 'dur')
            ui.startPlaying()
            ui.stdscr.clear()
        ui.verySafeQuit()
    ui.refresh()
    ui.mainLoop()

if __name__ == "__main__":
    main()


