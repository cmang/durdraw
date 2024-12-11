import configparser
import curses
import gzip
import os
import pdb
import pickle
import subprocess
import sys
import threading
from sys import version_info 
from durdraw.durdraw_options import Options
import durdraw.durdraw_file as durfile
import durdraw.durdraw_sauce as dursauce
import durdraw.log as log

class AppState():
    """ run-time app state, separate from movie options (Options()) """
    def __init__(self):

        # Check for optional dependencies
        #self.ansiLove = self.isAppAvail("ansilove")
        #self.neofetch = self.isAppAvail("neofetch")
        #self.PIL = self.checkForPIL()

        self.ansiLove = None
        self.neofetch = None
        self.PIL = None
        self.check_dependencies()

        #threading
        self.stop_event = threading.Event()
        self.bg_download_thread = None
        self.bg_download_executor = None
        # String containnig updates from threads to tell users about
        self.thread_update_string = None 
        self.pool_executor = None

        # User friendly defeaults
        self.quickStart = False
        self.mental = False # Mental mode - enable experimental options/features
        self.showStartupScreen = False
        self.narrowWindow = False
        self.curOpenFileName = ""
        python_version = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
        self.pyVersion = python_version
        self.colorMode = "256"  # or 16, or possibly "none" or "true" or "rgb" (24 bit rgb "truecolor")
        self.fileColorMode = None
        self.maxColors = 256
        self.iceColors = False

        # 16c stuff 
        self.sixteenc_available = True # Enabled if 16colo.rs browsing is available
        self.sixteenc_browsing = False   # Enabled if we are currently browsing 16c
        self.sixteenc_dizcache = {} # {"packname": dizdata} 
        self.sixteenc_cached_years = [] # [1996, etc]
        self.sixteenc_api = None
        self.sixteenc_year = None
        self.sixteenc_pack = None

        # Durview stuff
        self.durview_running = False

        self.play_queue = []    # List of files to switch between with 'n' and 'p' in Durview and/or play mode
        self.play_queue_position = None

        # Other durdraw runtime stuff
        self.can_inject = False # Allow injecting color codes to override ncurses colors (for BG 256 colors)
        self.sleep_time = 0     # Use this as a delay for playback mode, dictated in ui_curses.py from FPS
        self.showBgColorPicker = False # until BG colors work in 256 color mode. (ncurses 5 color pair limits)
        self.scrollColors = False   # When true, scroll wheel in canvas changes color instead of moving cursor
        self.editorRunning = True
        self.screenCursorMode = "default"   # can be block, underscore, pipe
        self.renderMouseCursor = False      # show Paint or Draw cursor in canvas
        self.validScreenCursorModes = ["default", "block", "underscore", "pipe"]
        self.cursorBlinks = True     # lord help me, why would anyone not want this to be true?
        self.totalFgColors = 16
        self.totalBgColors = 8
        self.defaultFgColor = 7
        self.defaultBgColor = 0
        self.width = 80     # default canvas width/columns
        self.height = 23    # default canvas height/lines
        self.wrapWidth = 80    # Default width to wrap at when loading ASCII files (.asc/.txt)
        self.minWindowWidth = 40    # smaller than this, and Durdraw complains that it can't draw the UI
        self.full_ui_width = 80   # smaller than this, and draw the streamlined UI
        self.stickyColorPicker = True # true to keep color picker on screen
        self.colorPickerSelected = False    # true when the user hits esc-c
        self.charEncoding = 'utf-8' # or cp437, aka ibm-pc
        self.unicodeBlockList = []
        self.characterSet = "Durdraw Default"
        self.showCharSetButton = False
        self.workingLoadDirectory = None
        self.fileShortPath = None
        self.fileLongPath = None
        # if self.characterSet == "Unicode Block" then Durdraw knows to use a
        # unicode block:
        #self.characterSet = "Unicode Block"
        self.unicodeBlock = "Braille Patterns"  # placeholder during initialization
        self.cursorMode = "Move"  # Move/Select, Draw and Color
        self.fetchMode = False    # use neofetch, replace {variables} in dur file
        self.fetchData = None       # a {} dict containing key:value for neofetch output.
        self.inferno = None
        self.inferno_opts = None
        self.playOnlyMode = False   # This means viewer mode now, actually..
        self.viewModeShowInfo = False   # show sauce etc in view mode
        self.playNumberOfTimes = 0  # 0 = loop forever, default
        self.undoHistorySize = 100  # How far back our undo history can
        self.playbackRange = (1,1)
        self.drawChar = '$'
        self.brush = None
        self.configFile = None
        self.configFileLoaded = False
        self.configFileName = None
        self.customThemeFile = None
        self.sauce = dursauce.SauceParser() # empty sauce
        #self.drawChar = b'\xE2\x96\x88'
        self.CP438_BLOCK = chr(219)
        self.UTF8_BLOCK = chr(9608)
        self.blockChar = self.UTF8_BLOCK      # Unicode block by default, --cp437 should change this
        self.colorPickChar = self.blockChar
        self.hasMouse = True # replace with equivalent curses.has_mouse()
        self.hasMouseScroll = True  # Disable for compatibility with older Python versions <3.10
        self.mouse_col = 0
        self.mouse_line = 0
        self.helpMov = None
        self.helpMov_2 = None
        self.hasHelpFile = False
        self.playingHelpScreen = False
        self.playingHelpScreen_2 = False    # on page 2 of help screen
        self.durVer = None
        self.debug = False
        self.debug2 = False     # extra verbose debug, eg: file loading intricates
        self.modified = False
        self.durhelp256_fullpath = None
        self.durhelp256_page2_fullpath = None
        self.durhelp16_fullpath = None
        self.durhelp16_page2_fullpath = None
        # This doesn't work yet (color pairs past 256 colors. They set, but the background color doesn't get set.
        #if sys.version_info >= (3, 10):
        #    if curses.has_extended_color_support(): # Requires Ncures 6
        #        self.showBgColorPicker = True   # until BG colors work in 256 color mode. (ncurses 5 color pair limits)
        self.realmaxX = 0
        self.realmaxY = 0
        self.topLine = 0    # the top line visible on the screen, used in refresh() for scrolling
        self.firstCol = 0    # leftmost visbile column, to facilitate left/right scrolling
        self.drawBorders = True
        self.durFileVer = 0     # gets set in main() from DUR_FILE_VER
        self.sideBarEnabled = True # to show color picker, sauce info, etc
        self.sideBarColumn = 0  # location, usually just right of the border
        #self.sideBar_minimum_width = 37 # Must have this much width to draw sidebar. Actually it's the colorBar width.
        self.sideInfo_minimum_width = 8 # Must have this much width beyond canvas width to draw esc-i sauce info
        self.sideBar_minimum_width = 5 # Must have this much width to draw sidebar. Actually it's the colorBar width.
        self.sideBar_minimum_width_256 = 37 # Must have this much width to draw sidebar. Actually it's the colorBar width.
        self.sideBar_minimum_width_16 = 12 # Must have this much width to draw sidebar. Actually it's the colorBar width.
        self.bottomBar_minimum_height = 10  # same as above, but for height
        self.bottomBar_minimum_height_256 = 10 
        self.bottomBar_minimum_height_16 = 4 
        self.colorBar_height = 8
        self.sideBarShowing = False
        self.themesEnabled = True
        self.themeName = "default"
        self.theme_16 = {
            'mainColor': 8,     # grey
            'clickColor': 3,     # green
            'clickHighlightColor': 11,     # bright green
            'borderColor': 8,     # grey
            #'notifications': 89     #  sick maroon
            'notificationColor': 8,     # grey
            'promptColor': 8,     # grey
            'menuItemColor': 2,
            'menuTitleColor': 3,
            'menuBorderColor': 4,
            }
        self.theme_256 = {
            'mainColor': 7,     # grey
            'clickColor': 2,     # green
            'clickHighlightColor': 10,     # bright green
            'borderColor': 7,     # grey
            #'notifications': 89     #  sick maroon
            'notificationColor': 3,     # cyan
            'promptColor': 3,     # cyan
            'menuItemColor': 7,
            'menuTitleColor': 98,
            'menuBorderColor': 7,
            }
        self.theme = self.theme_16
        self.log_level = 'WARNING'
        self.log_filepath = './durdraw.log'
        self.log_local_tz = False
        self.logger = log.getLogger('appstate')


    def maximize_canvas(self):
        term_size = os.get_terminal_size()
        if term_size[0] > 80:
           self.width = term_size[0]
        if term_size[1] > 24:
            self.height = term_size[1] - 2

    def check_dependencies(self):
        dependency_thread = threading.Thread(target=self.thread_check_dependencies)
        dependency_thread.start()

    def thread_check_dependencies(self):
        # Check for optional dependencies
        self.ansiLove = self.isAppAvail("ansilove")
        self.neofetch = self.isAppAvail("neofetch")
        self.PIL = self.checkForPIL()

    def setCursorModeMove(self):
        self.cursorMode="Move"

    def setCursorModeSelect(self):
        self.cursorMode="Select"

    def setCursorModeDraw(self):
        self.cursorMode="Draw"

    def setCursorModePaint(self):
        self.cursorMode="Paint"

    def setCursorModeCol(self):
        self.cursorMode="Color"

    def setCursorModeErase(self):
        self.cursorMode="Erase"

    def setCursorModeEyedrop(self):
        self.cursorMode="Eyedrop"

    def setDurFileVer(self, durFileVer):  # file format for saving. 1-4 are pickle, 5+ is JSON
       self.durFileVer = durFileVer

    def setDurVer(self, version):
        self.durVer = version

    def setDebug(self, isEnabled: bool):
        self.debug = isEnabled

    def setLogger(self, level=log.DEFAULT_LOG_LEVEL, filepath=log.DEFAULT_LOG_FILEPATH, local_tz=False):
        self.log_level = level
        self.log_filepath = filepath
        self.log_local_tz = local_tz
        self.logger = log.getLogger(
            'appstate',
            level=self.log_level,
            filepath=self.log_filepath,
            override=True,
            local_tz=self.log_local_tz,
        )

    def getLogger(self, name: str):
        return log.getLogger(name, level=self.log_level, filepath=self.log_filepath, local_tz=self.log_local_tz)

    def loadThemeList(self):
        """ Look for theme files in internal durdraw directory """
        # durhelp256_fullpath = pathlib.Path(__file__).parent.joinpath("help/durhelp-256-long.dur") 
        # Get a list of files from the themes paths
        internal_theme_path = pathlib.Path(__file__).parent.joinpath("themes/")
        self.internal_theme_file_list = glob.glob(f"{internal_theme_path}/*.dtheme.ini")
        #user_theme_path = pathlib.Path(__file__).parent.joinpath("themes/")
        #self.user_theme_file_list = glob.glob(f"{user_theme_path}/*.dtheme.ini")
        # Turn lists into an index of Theme name, Theme type, and Path to 
        available_themes = []   # populate with a list of dicts containing name=, path=, type=
        for filename in self.internal_theme_file_list:
            pass

    def loadConfigFile(self):
        # Load configuration filea
        configFullPath = os.path.expanduser("~/.durdraw/durdraw.ini")
        configShortFile  = 'durdraw.ini'
        configFileLocations = [configFullPath, configShortFile]
        configFile = configparser.ConfigParser()
        readConfigPaths = configFile.read(configFileLocations)
        if self.configFile == []:
            self.configFileLoaded = False
            return False 
        else:
            self.configFileName = readConfigPaths
            self.configFile = configFile
            self.configFileLoaded = True
            return True

    def loadThemeFromConfig(self, themeMode):
        #pdb.set_trace()
        if not self.themesEnabled:
            return False
        if 'Theme' in self.configFile:
            themeConfig = self.configFile['Theme']
            if 'theme-16' in themeConfig and themeMode == 'Theme-16':
                self.loadThemeFile(themeConfig['theme-16'], themeMode)
            if 'theme-256' in themeConfig and themeMode == 'Theme-256':
                self.loadThemeFile(themeConfig['theme-256'], themeMode)

    def getConfigOption(self, section: str, item: str):
        # section = something like [Main], item = something like color-mode:
        try:    # see if section and item exist, otherwise return False
            configSection = self.configFile[section]
            configItem = configSection[item]
            return configItem
        except KeyError:
            return False

    def loadThemeFile(self, themeFilePath, themeMode):
        # If there is a theme set, use it
        #if 'Theme' in self.configFile:
        # Load .dtheme file
        #themeFullPath = os.path.expanduser(f"~/.durdraw/{themeName}.dtheme")
        themeFullPath = os.path.expanduser(themeFilePath)
        themeFileConfig = configparser.ConfigParser()
        themeConfigsLoaded = themeFileConfig.read(themeFullPath)
        #pdb.set_trace()
        if themeConfigsLoaded == []:
            return False    # could not find or load the theme file
        else:
            theme = themeFileConfig[themeMode]
            if 'name' in theme:
                self.themeName = str(theme['name'])
            if 'mainColor' in theme:
                self.theme['mainColor'] = int(theme['mainColor'])
            if 'clickColor' in theme:
                self.theme['clickColor'] = int(theme['clickColor'])
            if 'borderColor' in theme:
                self.theme['borderColor'] = int(theme['borderColor'])
            if 'clickHighlightColor' in theme:
                self.theme['clickHighlightColor'] = int(theme['clickHighlightColor'])
            if 'notificationColor' in theme:
                self.theme['notificationColor'] = int(theme['notificationColor'])
            if 'promptColor' in theme:
                self.theme['promptColor'] = int(theme['promptColor'])
            if 'menuItemColor' in theme:
                self.theme['menuItemColor'] = int(theme['menuItemColor'])
            if 'menuTitleColor' in theme:
                self.theme['menuTitleColor'] = int(theme['menuTitleColor'])
            if 'menuBorderColor' in theme:
                self.theme['menuBorderColor'] = int(theme['menuBorderColor'])
            return True

    def checkForPIL(self):
        try:
            import PIL
            return True
        except ImportError:
            return False

    def isAppAvail(self, name):   # looks for program 'name' in path
        try:
            devnull = open(os.devnull)
            subprocess.Popen([name], stdout=devnull, stderr=devnull).communicate()
        except OSError as e:
            #if e.errno == os.errno.ENOENT:
            #    return False
            return False
        return True

    def loadDurFileToMov(self, fileName):
        """ Takes a file path, returns a movie object """
        fileName = os.path.expanduser(fileName)
        #self.helpMov = Movie(self.opts) # initialize a new movie to work with
        try:
            f = open(fileName, 'rb')
        except Exception as e:
            return False
        if (f.read(2) == b'\x1f\x8b'): # gzip magic number
            # file == gzip compressed
            f.close()
            try:
                f = gzip.open(fileName, 'rb')
            except Exception as e:
                return False
        else:
            f.seek(0)
        try:    # Load json help file
            #pdb.set_trace()
            loadedContainer = durfile.open_json_dur_file(f, self)
            opts = loadedContainer['opts']
            mov = loadedContainer['mov']
            return mov, opts
        except:
            #pass    # loading json help file failed for some reason, so...
            return False


    def loadHelpFileThread(self, helpFileName):
        help_loading_thread = threading.Thread(target=self.loadHelpFile, args=(helpFileName,))
        help_loading_thread.start()

    def loadHelpFile(self, helpFileName, page=1):
        helpFileName = os.path.expanduser(helpFileName)
        #self.helpMov = Movie(self.opts) # initialize a new movie to work with
        try:
            f = open(helpFileName, 'rb')
        except Exception as e:
            self.hasHelpFile = False
            self.helpMov = None
            return False
        if (f.read(2) == b'\x1f\x8b'): # gzip magic number
            # file == gzip compressed
            f.close()
            try:
                f = gzip.open(helpFileName, 'rb')
            except Exception as e:
                self.hasHelpFile = False
                self.helpMov = None
                self.helpMov_2 = None
                return False
        else:
            f.seek(0)
        try:    # Load json help file
            #pdb.set_trace()
            loadedContainer = durfile.open_json_dur_file(f, self)
            if page == 1:
                self.helpMovOpts = loadedContainer['opts']
                self.helpMov = loadedContainer['mov']
            elif page == 2:
                self.helpMovOpts_2 = loadedContainer['opts']
                self.helpMov_2 = loadedContainer['mov']
            self.hasHelpFile = True
            return True
        except:
            #pass    # loading json help file failed for some reason, so...
            return False
        #try:    # Load pickle file. This should never happen anymore, so...
        #    #self.opts = pickle.load(f)
        #    #self.mov = pickle.load(f)
        #    self.helpMovOpts = pickle.load(f)
        #    self.helpMov = pickle.load(f)
        #    self.hasHelpFile = True
        #    return True
        #except Exception as e:
        #    self.hasHelpFile = False
        #    self.helpMov = None
        #    return False



