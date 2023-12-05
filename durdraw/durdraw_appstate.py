import configparser
import curses
import gzip
import os
import pdb
import pickle
import subprocess
import sys
from durdraw.durdraw_options import Options
import durdraw.durdraw_file as durfile
import durdraw.durdraw_sauce as dursauce

class AppState():
    """ run-time app state, separate from movie options (Options()) """
    def __init__(self): # User friendly defeaults
        self.quickStart = False
        self.showStartupScreen = True
        self.curOpenFileName = ""
        self.colorMode = "256"  # or 16, or possibly "none" or "true" or "rgb" (24 bit rgb "truecolor")
        self.totalFgColors = "128"
        self.totalBgColors = "128"
        self.defaultFgColor = 7
        self.defaultBgColor = 0
        self.stickyColorPicker = True # true to keep color picker on screen
        self.colorPickerSelected = False    # true when the user hits esc-c
        self.charEncoding = 'utf-8' # or cp437, aka ibm-pc
        self.unicodeBlockList = []
        self.characterSet = "Durdraw Default"
        self.workingLoadDirectory = None
        # if self.characterSet == "Unicode Block" then Durdraw knows to use a
        # unicode block:
        #self.characterSet = "Unicode Block"
        self.unicodeBlock = "Braille Patterns"
        self.cursorMode = "Move"  # Move/Select, Draw and Color
        self.playOnlyMode = False
        self.playNumberOfTimes = 0  # 0 = loop forever, default
        self.ansiLove = self.isAppAvail("ansilove")
        self.PIL = self.checkForPIL()
        self.undoHistorySize = 100  # How far back our undo history can
        self.playbackRange = (1,1)
        self.drawChar = '$'
        self.configFile = None
        self.configFileLoaded = False
        self.configFileName = None
        self.customThemeFile = None
        self.sauce = dursauce.EmptySauce()
        #self.drawChar = b'\xE2\x96\x88'
        self.colorPickChar = chr(9608)  # unicode block character, for displaying colors in color pickers
        self.hasMouse = True # replace with equivalent curses.has_mouse()
        self.hasMouseScroll = True  # Disable for compatibility with older Python versions <3.10
        self.helpMov = None
        self.helpMov_2 = None
        self.hasHelpFile = False
        self.playingHelpScreen = False
        self.playingHelpScreen_2 = False    # on page 2 of help screen
        self.durVer = None
        self.debug = False
        self.modified = False
        self.durhelp256_fullpath = None
        self.durhelp256_page2_fullpath = None
        self.durhelp16_fullpath = None
        self.durhelp16_page2_fullpath = None
        self.showBgColorPicker = False  # until BG colors work in 256 color mode. (ncurses 5 color pair limits)
        # This doesn't work yet (color pairs past 256 colors. They set, but the background color doesn't get set.
        #if sys.version_info >= (3, 10):
        #    if curses.has_extended_color_support(): # Requires Ncures 6
        #        self.showBgColorPicker = True   # until BG colors work in 256 color mode. (ncurses 5 color pair limits)
        self.topLine = 0    # the top line visible on the screen, used in refresh() for scrolling
        self.firstCol = 0    # leftmost visbile column, to facilitate left/right scrolling
        self.drawBorders = True
        self.durFileVer = 0     # gets set in main() from DUR_FILE_VER
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

    def setCursorModeMove(self):
        self.cursorMode="Move"

    def setCursorModeSelect(self):
        self.cursorMode="Select"

    def setCursorModePnt(self):
        self.cursorMode="Draw"

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

