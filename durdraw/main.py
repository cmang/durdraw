# Part of Durdraw - https://github.com/cmang/durdraw
# main() entry point

import argparse
import configparser
import curses
import os
import sys
import time
import pathlib

from durdraw.durdraw_appstate import AppState
from durdraw.durdraw_ui_curses import UserInterface as UI_Curses
from durdraw.durdraw_options import Options
from durdraw.durdraw_version import DUR_VER
import durdraw.help
import durdraw.neofetcher as neofetcher

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

def main(fetch_args=None):
    DUR_FILE_VER = 7
    DEBUG_MODE = False # debug = makes debug_write available, sends verbose notifications
    durlogo = 'Durdraw'
    argChecker = ArgumentChecker()
    parser = argparse.ArgumentParser()
    parserStartScreenMutex = parser.add_mutually_exclusive_group()
    parserFilenameMutex = parser.add_mutually_exclusive_group()
    parserColorModeMutex = parser.add_mutually_exclusive_group()
    parserFilenameMutex.add_argument("filename", nargs='?', help=".dur or ascii file to load")
    parserFilenameMutex.add_argument("-p", "--play", help="Just play .dur, .ANS or .ASC file or files, then exit",
                    nargs='+')
    parser.add_argument("-d", "--delayexit", help="Wait X seconds after playback before exiting (requires -p)", nargs=1, type=float)
    parserStartScreenMutex.add_argument("-x", "--times", help="Play X number of times (requires -p)",
                    nargs=1, type=int)
    parserColorModeMutex.add_argument("--256color", help="Try 256 color mode", action="store_true", dest='hicolor')
    parserColorModeMutex.add_argument("--16color", help="Try 16 color mode", action="store_true", dest='locolor')
    parser.add_argument("-b", "--blackbg", help="Use a black background color instead of terminal default", action="store_true")
    parser.add_argument("-W", "--width", help="Set canvas width", nargs=1, type=int)
    parser.add_argument("-H", "--height", help="Set canvas height", nargs=1, type=int)
    parser.add_argument("-m", "--max", help="Maximum canvas size for terminal (overrides -W and -H)", action="store_true")
    parser.add_argument("--wrap", help="Number of columns to wrap lines at when loading ASCII and ANSI files (default 80)", nargs=1, type=int)
    parser.add_argument("--nomouse", help="Disable mouse support",
                    action="store_true")
    parser.add_argument("--cursor", help="Cursor mode (block, underscore, or pipe)", nargs=1)
    parser.add_argument("--notheme", help="Disable theme support (use default theme)",
                    action="store_true")
    parser.add_argument("--theme", help="Load a custom theme file", nargs=1)
    #parser.add_argument("-A", "--ibmpc", "--cp437", help="Use Code Page 437 (IBM-PC/MS-DOS) block character encoding instead of Unicode. (Needs CP437 capable terminal and font)", action="store_true")
    parser.add_argument("--cp437", help="Display extended characters on the screen using Code Page 437 (IBM-PC/MS-DOS) encoding instead of Utf-8. (Requires CP437 capable terminal and font) (beta)", action="store_true")
    parser.add_argument("--export-ansi", action="store_true", help="Export loaded art to an .ansi file and exit")
    parser.add_argument("-u", "--undosize", help="Set the number of undo history states - default is 100. More requires more RAM, less saves RAM.", nargs=1, type=int)
    #--mental -- Enable experimental (not ready for prime time) options
    parser.add_argument("--mental", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--fetch", help="Replace fetch strings with Neofetch output", action="store_true")
    parser.add_argument("-V", "--version", help="Show version number and exit",
                    action="store_true")
    parser.add_argument("--debug", action="store_true", help=argparse.SUPPRESS)
            
    args = parser.parse_args(fetch_args)

    if args.version:
        print(DUR_VER)
        exit(0)
    if args.times and not args.play:
        print("-x option requires -p")
        exit(1)

    # Initialize application
    app = AppState()    # to store run-time preferences from CLI, environment stuff, etc.
    app.setDurVer(DUR_VER)
    app.setDurFileVer(DUR_FILE_VER)
    app.setDebug(DEBUG_MODE)
    term_size = os.get_terminal_size()

    # Parse general command-line paramaters
    if args.debug:
        app.setDebug(True)
    if args.undosize: 
        app.undoHistorySize = int(args.undosize[0])
    #if args.width and args.width[0] > 80 and args.width[0] < term_size[0]:
    if args.width and args.width[0] > 1 and args.width[0] < term_size[0]:
        app.width = args.width[0]
    #if args.height and args.height[0] > 24 and args.height[0] < term_size[1]:
    if args.height and args.height[0] > 1 and args.height[0] < term_size[1]:
        app.height = args.height[0]
    if args.max:
        app.maximize_canvas()
    if args.wrap:
        app.wrapWidth = args.wrap[0]
    app.showStartupScreen=False
    app.quickStart = True
    if args.nomouse:
        app.hasMouse = False
    if args.notheme:
        app.themesEnabled = False
    if args.hicolor:
        app.colorMode = "256"
    if args.locolor:
        app.colorMode = "16"
    if args.cp437:
        app.charEncoding = 'cp437'
        #app.drawChar = '$'
        app.colorPickChar = app.CP438_BLOCK  # ibm-pc/cp437 ansi block character
        app.blockChar = app.CP438_BLOCK
        app.drawChar = app.CP438_BLOCK
    else:
        app.charEncoding = 'utf-8'
    durhelp_fullpath = pathlib.Path(__file__).parent.joinpath("help/durhelp.dur")
    if args.blackbg:
        app.blackbg = False
    else: app.blackbg = True

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
            if 'max-canvas' in mainConfig:
                if mainConfig.getboolean('max-canvas'):
                    app.maximize_canvas()
            if 'cursor-mode' in mainConfig:
                app.screenCursorMode = mainConfig['cursor-mode']
            if 'scroll-colors' in mainConfig:
                if mainConfig.getboolean('scroll-colors'):
                    app.scrollColors = True
            if 'mental-mode' in mainConfig:
                app.mental = True
        # load theme set in config fileFalse
        if app.colorMode == "256":
            app.loadThemeFromConfig("Theme-256")
        else:
            app.loadThemeFromConfig("Theme-16")

    if 'Logging' in app.configFile:
        logging_config = dict(app.configFile['Logging'])

        if 'local-tz' in logging_config:
            logging_config['local_tz'] = app.configFile['Logging'].getboolean('local-tz')
            del logging_config['local-tz']

        app.setLogger(**logging_config)

    if args.theme:
        if app.colorMode == "256":
            app.loadThemeFile(args.theme[0], "Theme-256")
        else:
            app.loadThemeFile(args.theme[0], "Theme-16")
        app.customThemeFile = args.theme[0]

    if args.cursor:
        if args.cursor[0] in app.validScreenCursorModes:
            app.screenCursorMode = args.cursor[0]
        else:
            print("--cursor option requires one of the following: block, underscore, pipe")
            exit(1)

    # Load help file - first look for resource path, eg: python module dir
    durhelp_fullpath = ''
    #durhelp_fullpath = pathlib.Path(__file__).parent.joinpath("help/durhelp.dur")
    durhelp256_fullpath = pathlib.Path(__file__).parent.joinpath("help/durhelp-256-long.dur")
    #durhelp256_fullpath = pathlib.Path(__file__).parent.joinpath("help/durhelp-256-page1.dur")
    #durhelp256_page2_fullpath = pathlib.Path(__file__).parent.joinpath("help/durhelp-256-page2.dur")
    durhelp16_fullpath = pathlib.Path(__file__).parent.joinpath("help/durhelp-16-long.dur")
    #durhelp16_fullpath = pathlib.Path(__file__).parent.joinpath("help/durhelp-16-page1.dur")
    #durhelp16_page2_fullpath = pathlib.Path(__file__).parent.joinpath("help/durhelp-16-page2.dur")
    app.durhelp256_fullpath = durhelp256_fullpath
    #app.durhelp256_page2_fullpath = durhelp256_page2_fullpath
    app.durhelp16_fullpath = durhelp16_fullpath
    #app.durhelp16_page2_fullpath = durhelp16_page2_fullpath
    #app.loadHelpFile(durhelp_fullpath)
    #app.loadHelpFile(durhelp16_fullpath)
    #app.loadHelpFile(durhelp16_page2_fullpath, page=2)
    #if not app.hasHelpFile:
    #    durhelp_fullpath = 'durdraw/help/durhelp.dur'
    #    app.loadHelpFile(durhelp_fullpath)

    if app.showStartupScreen:
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
        if app.configFileLoaded:
            print(f"Configuration file found: {app.configFileName}")
        else:
            print(f"Configuration file not found.")

        if app.themesEnabled:
            print(f"Theme: {app.themeName}")
        else:
            print(f"Theme: Default (none)")

        print("Undo history size = %d" % app.undoHistorySize)
        print("Canvas size: %i columns, %i lines" % (app.width, app.height))
        if args.wait:
            try:
                choice = input("Press Enter to Continue...")
            except KeyboardInterrupt:
                print("\nCaught interrupt, exiting.")
                exit(0)
        else:
            pass
            time.sleep(3)
    if args.play:
        app.playOnlyMode = True
        app.editorRunning = False

    if args.mental:
        # Enable exprimental options
        app.mental = True

    if args.fetch:
        #app.playOnlyMode = True
        app.fetchMode = True
        app.fetchData = neofetcher.run()
        #app.editorRunning = False
        #app.drawBorders = False
    #ui = curses.wrapper(UI_Curses, app)
    ui = UI_Curses(app)
    if app.hasMouse:
        ui.initMouse()
    if app.blackbg:
        ui.enableTransBackground()
    if args.filename:
        ui.loadFromFile(args.filename, 'dur')
    if args.play or args.fetch:
        # Just play files and exit
        app.drawBorders = False
        if args.times:
            app.playNumberOfTimes = args.times[0]
        for movie in args.play:
            ui.stdscr.clear()
            ui.loadFromFile(movie, 'dur')
            if app.fetchMode:
                ui.replace_neofetch_keys()
            ui.startPlaying()
        if args.delayexit:
            time.sleep(args.delayexit[0])
        ui.verySafeQuit()
    if args.export_ansi:
        # Export ansi and exit
        ui.saveAnsiFile(os.path.splitext(args.filename)[0] + ".ansi", encoding=app.charEncoding)
        ui.verySafeQuit()
    ui.refresh()
    ui.mainLoop()

if __name__ == "__main__":
    main()


