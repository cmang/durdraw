# This file needs to have all of its non-curses code moved into separate files/libraries

import curses
import curses.panel
import fnmatch
import glob
import gzip
import locale
import os
import os.path
import pdb
import pickle
import shutil
import sys
import subprocess
import time
from PIL import Image

#from durdraw.durdraw_appstate import AppState
from durdraw.durdraw_options import Options
from durdraw.durdraw_color_curses import AnsiArtStuff
from durdraw.durdraw_movie import Movie
from durdraw.durdraw_undo import UndoManager
import durdraw.durdraw_file as durfile
from durdraw.durdraw_ui_widgets import StatusBar
import durdraw.durdraw_gui_manager as durgui
import durdraw.durdraw_movie as durmovie
import durdraw.durdraw_color_curses as dur_ansilib
import durdraw.durdraw_ansiparse as dur_ansiparse
import durdraw.durdraw_charsets as durchar

class UserInterface():  # Separate view (curses) from this controller
    """ Draws user interface, has main UI loop. """
    #def __init__(self, stdscr, app):
    def __init__(self, app):
        # Set cursor shape to block
        sys.stdout.write(f"\x1b[1 q")
        self.opts = Options(width=app.width, height=app.height)
        self.appState = app # will be filled in by main() .. run-time app state stuff
        self.clipBoard = None   # frame object
        self.charMapNumber = 0
        self.chMap = {}
        self.chMapString = ""
        self.statusBar = None
        self.appState.unicodeBlockList = durchar.get_unicode_blocks_list()
        self.initCharSet()  # sometimes later options can store a char set to init - utf-8, cp437, etc.
        os.environ.setdefault('ESCDELAY', '10')
        # initialize screen and draw the 'canvas'
        locale.setlocale(locale.LC_ALL, '')    # set your locale
        self.realstdscr = curses.initscr()
        realmaxY,realmaxX = self.realstdscr.getmaxyx() # test size
        self.statusBarLineNum = realmaxY - 2
        self.stdscr = curses.newwin(realmaxY, realmaxX, 0, 0)   # Curses window
        self.panel = curses.panel.new_panel(self.stdscr)    # Panel for drawing, to sit below menus
        self.panel.bottom()
        self.panel.show()
        self.pressingButton = False
        self.playingHelpScreen = False
        self.pushingToClip = False  # true while we are holding down mouse button to draw or erase
        self.metaKey = 0
        self.commandMode = False
        self.line_1_offset = 5
        self.transportOffset = 0
        #self.stdscr.box()
        self.gui = durgui.Gui(guiType="curses", window=self.stdscr)
        curses.start_color()    # Yeayuhhh
        self.ansi = AnsiArtStuff(self.appState)   # obj for misc ansi-related stuff
        if self.appState.colorMode == "256":
            if self.ansi.initColorPairs_256color():
                self.appState.theme = self.appState.theme_256
                self.appState.loadThemeFromConfig('Theme-256')
                if self.appState.customThemeFile:
                    self.appState.loadThemeFile(self.appState.customThemeFile, 'Theme-256')
                if self.appState.playOnlyMode == False:
                    self.appState.loadHelpFile(self.appState.durhelp256_fullpath)
                    self.appState.loadHelpFile(self.appState.durhelp256_page2_fullpath, page=2)
            else:
                self.appState.colorMode = "16"
                self.appState.theme = self.appState.theme_16
                self.appState.loadThemeFromConfig('Theme-16')
                if self.appState.playOnlyMode == False:
                    self.appState.loadHelpFile(self.appState.durhelp16_fullpath)
                    self.appState.loadHelpFile(self.appState.durhelp16_page2_fullpath, page=2)
                if self.appState.customThemeFile:
                    self.appState.loadThemeFile(self.appState.customThemeFile, 'Theme-256')
        if self.appState.colorMode == "16":
            self.ansi.initColorPairs_cga()
        if not app.quickStart and app.showStartupScreen:
            print(f"Color mode: {self.appState.colorMode}")
            time.sleep(2)
        self.colorfg = 7    # default fg white
        if self.appState.colorMode == '256':
            self.colorbg = 0    # default bg black
            self.colorfg = 7    # default fg white
        else:
            self.colorfg = 8    # default fg white
            self.colorbg = 8    # default bg black
        self.colorpair = self.ansi.colorPairMap[(self.colorfg, self.colorbg)] # set ncurss color pair
        self.mov = Movie(self.opts) # initialize a new movie to work with
        self.undo = UndoManager(self, appState = self.appState)   # initialize undo/redo system
        self.undo.setHistorySize(self.appState.undoHistorySize)
        self.xy = [0, 1]     # cursor position x/y - was "curs"
        self.playing = False
        curses.noecho()
        curses.raw()
        curses.nonl()
        self.stdscr.keypad(1)
        self.realmaxY,self.realmaxX = self.realstdscr.getmaxyx()
        self.testWindowSize()
        self.statusBar = StatusBar(self, x=self.statusBarLineNum, y=0, appState=self.appState)
        if self.appState.playOnlyMode:
            self.statusBar.hide()
        else:
            for button in self.statusBar.buttons:
                self.gui.add_button(button)
        self.setWindowTitle("Durdraw")

        # set a default drawing character
        self.appState.drawChar = chr(self.chMap['f4'])
        self.statusBar.drawCharPickerButton.label = self.appState.drawChar

        self.statusBarLineNum = self.realmaxY - 2

    def initMouse(self):
        curses.mousemask(1)     # click response without drag support
        curses.mousemask(curses.REPORT_MOUSE_POSITION | curses.ALL_MOUSE_EVENTS)
        #print('\033[?1003h') # enable mouse tracking with the XTERM API
        # https://invisible-island.net/xterm/ctlseqs/ctlseqs.html#h2-Mouse-Tracking

    def enableTransBackground(self):
        curses.use_default_colors()
        if self.appState.colorMode == '16':
            self.ansi.initColorPairs_cga(trans=True)
        else:
            #curses.init_pair(1, 16, -1)     # black
            curses.init_pair(1, 4, -1)  # blue 
            curses.init_pair(2, 2, -1)  # green
            curses.init_pair(3, 6, -1)  # cyan
            curses.init_pair(4, 1, -1)  # red
            curses.init_pair(5, 5, -1)  # magenta
            curses.init_pair(6, 3, -1)  # yellow
            curses.init_pair(7, 15, -1) # white
            curses.init_pair(8, 8, -1)  # dark grey/bright black
            curses.init_pair(9, 12, -1) # bright blue
            curses.init_pair(10, 10, -1) # bright green
            curses.init_pair(11, 14, -1) # bright cyan
            curses.init_pair(12, 9, -1) # bright red
            curses.init_pair(13, 13, -1) # bright magenta
            curses.init_pair(14, 11, -1) # bright yellow
            curses.init_pair(15, 15, -1) # bright white
            

    def setWindowTitle(self, title):
        title = f"Durdraw - {title}"
        sys.stdout.write(f"\x1b]2;{title}\x07")

    def getPlaybackRange(self):
        """ ask for playback range presses cmd-r """
        self.clearStatusLine()
        self.move(self.mov.sizeY, 0)
        self.stdscr.nodelay(0) # wait for input when calling getch
        goodResponse = False
        while goodResponse == False:
            self.promptPrint("Start frame for playback [currently %i of %i, 0 for All]: " % \
                (self.appState.playbackRange[0], self.mov.frameCount))
            curses.echo()
            lowRange = self.stdscr.getstr()
            if lowRange.isdigit():
                lowRange = int(lowRange)
                if lowRange >= 0 and lowRange <= self.mov.frameCount:
                    goodResponse = True
                else:
                    self.notify("Must be a number between %i and %i" % (1, self.mov.frameCount))
                    goodResponse = False
            else:
                self.notify("Playback range not changed.")
                curses.noecho()
                if self.playing:
                    self.stdscr.nodelay(1) # don't wait for input when calling getch
                return False
        if lowRange == 0:
            self.setPlaybackRange(1, self.mov.frameCount)
            curses.noecho()
            if self.playing:
                self.stdscr.nodelay(1) # don't wait for input when calling getch
            return True
        goodResponse = False
        self.clearStatusLine()
        while goodResponse == False:
            self.promptPrint("End frame for playback [currently %i of %i]: " % \
                (self.appState.playbackRange[0], self.mov.frameCount))
            curses.echo()
            highRange = self.stdscr.getstr()
            if highRange.isdigit():
                highRange = int(highRange)
                if highRange >= lowRange and highRange <= self.mov.frameCount:
                    goodResponse = True
                else:
                    self.notify("Must be a number between %i and %i" % (lowRange, self.mov.frameCount))
                    goodResponse = False
            else:
                self.notify("Playback range not changed.")
                curses.noecho()
                if self.playing:
                    self.stdscr.nodelay(1) # don't wait for input when calling getch
                return False
        self.setPlaybackRange(lowRange, highRange)
        curses.noecho()
        if self.playing:
            self.stdscr.nodelay(1) # don't wait for input when calling getch
        return True
    

    def setPlaybackRange(self, start, stop):
        self.appState.playbackRange = (start, stop)

    def gotoFrameGetInput(self):
        self.clearStatusLine()
        self.move(self.mov.sizeY, 0)
        self.stdscr.nodelay(0) # wait for input when calling getch
        goodResponse = False
        while goodResponse == False:
            self.promptPrint("Enter frame to go to [currently %i of %i]: " % \
                (self.mov.currentFrameNumber, self.mov.frameCount))
            curses.echo()
            newFrameNumber = self.stdscr.getstr()
            if newFrameNumber.isdigit():
                newFrameNumber = int(newFrameNumber)
                if newFrameNumber >= 0 and newFrameNumber <= self.mov.frameCount:
                    goodResponse = True
                else:
                    self.notify("Must be a number between %i and %i" % (1, self.mov.frameCount))
                    goodResponse = False
            else:
                self.notify("Current frame number not changed.")
                curses.noecho()
                if self.playing:
                    self.stdscr.nodelay(1) # don't wait for input when calling getch
                return False
        if goodResponse:
            self.mov.gotoFrame(newFrameNumber)
        curses.noecho()

    def setAppState(self, appState):
        """ Takes the app state (running config options) and makes any changes
            needed to the UI/etc to honor that app state """
        self.appState = appState
        # set undo history size
        self.undo.setHistorySize(self.appState.undoHistorySize)

    def setFgColor(self, fg):
        self.colorfg = fg
        self.colorpair = self.ansi.colorPairMap[(self.colorfg, self.colorbg)] 

    def setBgColor(self, bg):
        self.colorbg = bg
        self.colorpair = self.ansi.colorPairMap[(self.colorfg, self.colorbg)] 

    def switchTo16ColorMode(self):
        self.switchToColorMode("16")

    def switchTo256ColorMode(self):
        self.switchToColorMode("256")

    def switchToColorMode(self, newMode: str):
        """ newMode, eg: '16' or '256' """
        if newMode == "16":
            self.ansi.initColorPairs_cga()
            self.appState.colorMode = "16"
            self.appState.loadThemeFromConfig("Theme-16")
            self.statusBar.charSetButton.hide()
            #if self.statusBar.colorPickerEnabled:
            #    self.statusBar.enableColorPicker()
        if newMode == "256":
            self.ansi.initColorPairs_256color()
            self.appState.colorMode = "256"
            self.appState.loadThemeFromConfig("Theme-256")
            self.statusBar.charSetButton.show()
            #if not self.statusBar.colorPickerEnabled:
            #    self.statusBar.disableColorPicker()

    def nextFgColor(self):
        """ switch to next fg color, cycle back to beginning at max """
        if self.appState.colorMode == "256":
            if self.colorfg < 255:
                newColor = self.colorfg + 1
            else:
                newColor = 1
        elif self.appState.colorMode == "16":
            if self.colorfg < 16:
                newColor = self.colorfg + 1
            else:
                newColor = 1
        self.setFgColor(newColor)

    def prevFgColor(self):
        """ switch to prev fg color, cycle around to end if at beginning """
        if self.colorfg > 1:
            newColor = self.colorfg - 1
        else:
            if self.appState.colorMode == "16":
                newColor = 16
            elif self.appState.colorMode == "256":
                newColor = 255
            else:
                newColor = 16   # default to 16 color
        self.setFgColor(newColor)

    def nextBgColor(self):
        """ switch to the next bg color, cycle around if at beginning """
        if self.appState.colorMode == "256":
            pass
        elif self.appState.colorMode == "16":
            if self.colorbg < 8:
                newColor = self.colorbg + 1
                if (self.colorfg == 7 and self.colorbg == 7) or (self.colorfg == 15 and self.colorbg == 7):  # skip over red on red
                    newColor = self.colorbg + 1
            else:
                newColor = 1
            self.setBgColor(newColor)

    def prevBgColor(self):
        """ switch to prev bg color, cycle around to end if at beginning """
        if self.appState.colorMode == "256":
            pass
        else:
            if self.colorbg > 1:
                newColor = self.colorbg - 1
                if self.colorfg == 7 and self.colorbg == 7 or self.colorfg == 15 and self.colorbg == 7:  # skip over red on red
                    newColor = self.colorbg - 1
            else:
                newColor = 8
            self.setBgColor(newColor)

    def cursorOff(self):
        try:
            curses.curs_set(0)  # turn off cursor
        except curses.error:
            pass    # .. if terminal supports it.

    def cursorOn(self):
        try:
            curses.curs_set(1)  # turn on cursor
        except curses.error:
            pass    # .. if terminal supports it.

    def addstr(self, y, x, str, attr=None): # addstr(y, x, str[, attr]) and addstr(str[, attr])
        """ Wraps ncurses addstr in a try;except, prevents addstr from
            crashing cureses if it fails """
        if not attr:
            try:
                if self.appState.charEncoding == 'utf-8':
                    self.stdscr.addstr(y, x, str.encode('utf-8'))
                else:
                    self.stdscr.addstr(y, x, str)
            except curses.error:
                self.testWindowSize()
        else:
            try:
                if self.appState.charEncoding == 'utf-8':
                    self.stdscr.addstr(y, x, str.encode('utf-8'), attr)
                else:
                    self.stdscr.addstr(y, x, str, attr)
            except curses.error:
                self.testWindowSize()

    def move(self, y, x):
        realLine = y - self.appState.topLine
        try:
            self.stdscr.move(realLine, x)
        except curses.error:
            self.testWindowSize()

    def notify(self, message, pause=False):
        self.cursorOff()
        self.clearStatusLine()
        self.addstr(self.statusBarLineNum, 0, message, curses.color_pair(self.appState.theme['notificationColor']))
        self.stdscr.refresh()
        if pause:
            if self.playing:
                self.stdscr.nodelay(0) # wait for input when calling getch
                self.stdscr.getch()
                self.stdscr.nodelay(1) # do not wait for input when calling getch   
            else:
                self.stdscr.getch()
        if not pause:
            curses.napms(1500)
            curses.flushinp()
        self.clearStatusLine()
        self.cursorOn()
        self.stdscr.refresh()

    def testWindowSize(self):
        """Test to see if window == too small for program to operate, and
        go into small window mode if necessary"""
        realmaxY, realmaxX = self.realstdscr.getmaxyx() # test size
        if realmaxY != self.realmaxY or realmaxX != self.realmaxX:
            self.resizeHandler()
        self.realmaxY, self.realmaxX = realmaxY, realmaxX
        while self.realmaxX < 80:
            self.smallWindowMode()   # go into small window loop.stdscr

    def smallWindowMode(self):
        """Clear the screen, draw a small message near 0,0 that the window
        == too small.  Keep doing so until the screen == resized larger."""
        self.stdscr.clear()
        self.stdscr.refresh()
        self.realmaxY,self.realmaxX = self.realstdscr.getmaxyx()
        while self.realmaxX < self.mov.sizeX:
            try:
                self.addstr(0, 0, "Terminal is too small for the UI.")
                self.addstr(1, 0, "Please enlarge to 80 columns or larger, or press 'q' to quit")
            except:     # if window is too small for the message ^
                pass
            c = self.stdscr.getch()
            if c == 113:  # 113 == 'q'
                self.verySafeQuit()
            self.realmaxY,self.realmaxX = self.realstdscr.getmaxyx()
            self.stdscr.refresh()
            time.sleep(0.02)
        self.stdscr.refresh()
        self.stdscr.clear()
        #self.testWindowSize()

    def backspace(self):
        if self.xy[1] > 1:
            self.undo.push()
            self.xy[1] = self.xy[1] - 1
            if self.playing:
                self.insertChar(ord(' '), fg=1, bg=0, frange=self.appState.playbackRange)
            else:
                self.insertChar(ord(' '), fg=1, bg=0)
            self.xy[1] = self.xy[1] - 1

    def deleteKeyPop(self, frange=None):
        if self.xy[1] > 0:
            self.undo.push()
            if frange:  # framge range
                for frameNum in range(frange[0] - 1, frange[1]):
                    self.mov.frames[frameNum].content[self.xy[0]].pop(self.xy[1] - 1)     # line & add a blank
                    self.mov.frames[frameNum].content[self.xy[0]].append(' ')         # at the end of each line.
                    self.mov.frames[frameNum].newColorMap[self.xy[0]].pop(self.xy[1] - 1)     # line & add a blank
                    self.mov.frames[frameNum].newColorMap[self.xy[0]].append([1,0])         # at the end of each line.
            else:
                self.mov.currentFrame.content[self.xy[0]].pop(self.xy[1] - 1)
                self.mov.currentFrame.content[self.xy[0]].append(' ')
                self.mov.currentFrame.newColorMap[self.xy[0]].pop(self.xy[1] - 1)
                self.mov.currentFrame.newColorMap[self.xy[0]].append([1,0])         # at the end of each line.


    def insertColor(self, fg=1, bg=0, frange=None, x=None, y=None, pushUndo=True):
        """ Sets the color for an x/y location on the current frame,
        or a range of frames """
        if pushUndo:    # push onto the clipboard stack
            self.undo.push()
        if x == None:
            x = self.xy[1]
        if y == None:
            y = self.xy[0]
        if frange:
            for fn in range(frange[0] - 1, frange[1]):
                self.mov.frames[fn].newColorMap[y][x - 1] = [fg, bg]
        else:
            self.mov.currentFrame.newColorMap[y][x - 1] = [fg, bg]
        #self.mov.currentFrame.newColorMap[self.xy[0]][self.xy[1] - 1] = [self.colorfg, self.colorbg]

    def insertChar(self, c, fg=1, bg=0, frange=None, x=None, y=None, moveCursor = False, pushUndo=True):
        """ insert character at current location, move cursor to the right (unless at the edge of canvas) """
        if pushUndo:    # push onto the clipboard stack
            self.undo.push()
        if x == None:
            x = self.xy[1]
            moveCursor = True
        if y == None:
            y = self.xy[0]
        if frange: # frame range
            for fn in range(frange[0] - 1, frange[1]):
                self.mov.frames[fn].content[y][x - 1] = chr(c)
                #self.mov.frames[fn].colorMap.update(
                #        {(y,x - 1):(fg,bg)} )
                self.mov.frames[fn].newColorMap[y][x - 1] = [fg, bg]
            if x < self.mov.sizeX and moveCursor:
                self.xy[1] = self.xy[1] + 1 
        else:
            self.mov.currentFrame.content[y][x - 1] = chr(c)
            #self.mov.currentFrame.colorMap.update(
            #        {(y,x - 1):(fg,bg)} )
            self.mov.currentFrame.newColorMap[y][x - 1] = [fg, bg]
            if x < self.mov.sizeX and moveCursor:
                self.xy[1] = self.xy[1] + 1 

    def eyeDrop(self, col, line):
        old_fg = self.colorfg
        old_bg = self.colorbg
        fg, bg = self.mov.currentFrame.newColorMap[line][col]
        fg, bg = self.mov.currentFrame.newColorMap[line][col]
        try:
            self.setFgColor(fg)
            self.setBgColor(bg)
        except:
            self.setFgColor(old_fg)
            self.setBgColor(old_bg)

    def clearCanvasPrompt(self):
        self.clearCanvas(prompting=True)

    def clearCanvas(self, prompting = False):
        clearing = True  # assume we are clearing unless we prompt and say "n"
        if prompting:
            self.stdscr.nodelay(0) # wait for input when calling getch
            self.clearStatusLine()
            self.promptPrint("Are you sure you want to clear the canvas? (Y/N) " )
            while prompting:
                time.sleep(0.01)
                c = self.stdscr.getch()
                if c == 121:   # 121 = y
                    clearing = True
                    prompting = False
                elif c == 110: # 110 = n
                    clearing = False
                    prompting = False
            self.clearStatusLine()
        if clearing:
            #self.undo.push() # so we can undo this operation
            self.mov = Movie(self.opts) # initialize a new movie
            self.setPlaybackRange(1, self.mov.frameCount)
            self.undo = UndoManager(self, appState = self.appState) # reset undo system

    def showTransformer(self):
        """ Let the user pick transformations: Bounce, Repeat, Reverse """
        self.clearStatusLine()
        prompting = True
        while prompting:
            self.promptPrint("[B]ounce, [R]epeat, or Re[v]erse?")
            c = self.stdscr.getch()
            if c in [98]:  # b - bounce |> -> |><|
                prompting = False
            if c in [114]:  # r - repeat |> -> |>|>
                prompting = False
                self.transform_repeat()
            if c in [118]:  # v - reverse |> -> <|
                prompting = False
                self.transform_reverse()
            if c in [27]: # escape - cancel
                prompting = False

    def transform_repeat(self):
        """ |>|> Clone all the frames in the range so they repeat once """
        pass

    def transform_reverse(self):
        pass

    def moveCurrentFrame(self):
        self.undo.push()
        prompting = True
        self.clearStatusLine()
        startPosition = self.mov.currentFrameNumber
        newPosition = self.mov.currentFrameNumber
        while prompting:
            time.sleep(0.01)
            self.promptPrint("Use left/right to move frame, press Enter when done or Esc to cancel. (%i/%i)" % (newPosition, self.mov.frameCount))
            c = self.stdscr.getch()
            if c in [98, curses.KEY_LEFT]:
                # move frame left one position (use pop and push)
                if newPosition == 1: # if at first
                    newPosition = self.mov.frameCount # go to end
                else:
                    newPosition -= 1
            elif c in [102, curses.KEY_RIGHT]:
                if newPosition == self.mov.frameCount: # if at last
                    newPosition = 1 # go back to beginning
                else:
                    newPosition += 1
            elif c in [13, curses.KEY_ENTER]: # enter - save  new position
                self.mov.moveFramePosition(startPosition, newPosition)
                self.mov.gotoFrame(newPosition)
                prompting = False
            elif c in [27]: # escape - cancel
                self.undo.undo()
                prompting = False

    def increaseFPS(self):
        if self.opts.framerate != 50: # max 50fps
            self.opts.framerate += 1

    def decreaseFPS(self):
        if self.opts.framerate != 1.0: # min 1fps
            self.opts.framerate -= 1

    def showAnimatedHelpScreen(self, page=1):
        self.appState.drawBorders = False
        wasPlaying = self.playing   # push, to pop when we're done
        oldTopLine = self.appState.topLine  # dito
        oldFirstCol = self.appState.firstCol    # dito
        self.appState.topLine = 0
        self.appState.firstCol = 0
        self.playing = False
        self.stdscr.nodelay(1) # do not wait for input when calling getch
        last_time = time.time()
        self.cursorOff()
        self.playingHelpScreen = True
        self.appState.playingHelpScreen = True
        if page == 2:
            self.appState.playingHelpScreen_2 = True
        else:
            self.appState.playingHelpScreen_2 = False
        playedTimes=1
        new_time = time.time()
        if page == 2:
            helpMov = self.appState.helpMov_2
        else:
            helpMov = self.appState.helpMov
        if page == 1:
            sleep_time = (1000.0 / self.appState.helpMovOpts.framerate) / 1000.0
        elif page == 2:
            sleep_time = (1000.0 / self.appState.helpMovOpts_2.framerate) / 1000.0
        helpMov.gotoFrame(1)
        self.stdscr.clear()
        self.clearStatusLine()
        self.promptPrint("* Press the any key (or click) to continue *")
        clickColor = self.appState.theme['clickColor']
        promptColor = self.appState.theme['promptColor']
        self.addstr(self.statusBarLineNum - 1, 0, "You can use ALT or META instead of ESC. Everything this color is clickable", curses.color_pair(promptColor))
        self.addstr(self.statusBarLineNum - 1, 51, "this color", curses.color_pair(clickColor) | curses.A_BOLD)
        self.addstr(self.statusBarLineNum - 1, 65, "clickable", curses.color_pair(clickColor) | curses.A_BOLD)
        while self.playingHelpScreen:
            self.move(self.xy[0], self.xy[1])
            self.refresh()
            if page == 2:
                self.addstr(12, 51, f"{self.appState.durVer}", curses.color_pair(promptColor))
                self.addstr(13, 54, f"{self.appState.colorMode}", curses.color_pair(promptColor))
                self.addstr(14, 62, f"{self.appState.charEncoding}", curses.color_pair(promptColor))
            c = self.stdscr.getch()
            if c != -1:   # -1 means no keys are pressed.
                self.playingHelpScreen = False
            new_time = time.time()
            frame_delay = helpMov.currentFrame.delay
            if frame_delay > 0:
                realDelayTime = frame_delay
            else:
                realDelayTime = sleep_time
            if new_time >= (last_time + realDelayTime): # Time to update the frame? If so...
                last_time = new_time
                # draw animation
                if helpMov.currentFrameNumber == helpMov.frameCount:
                    helpMov.gotoFrame(1)
                else:
                    helpMov.nextFrame()
            else:
                time.sleep(0.008) # to keep from sucking up cpu
        if not wasPlaying:
            self.stdscr.nodelay(0) # back to wait for input when calling getch
        self.cursorOn()
        self.appState.playingHelpScreen = False
        self.appState.playingHelpScreen_2 = False
        self.playingHelpScreen = False
        self.stdscr.clear()
        self.playing = wasPlaying
        self.topLine = oldTopLine
        self.firstCol = oldFirstCol
        self.appState.drawBorders = True

    def startPlaying(self):
        """ Start playing the animation - start a "game" style loop, make FPS
            by drawing if current time == greater than a delta plus the time
            the last frame was drawn.
        """
        self.stdscr.nodelay(1) # do not wait for input when calling getch
        last_time = time.time()
        self.statusBar.toolButton.hide()
        self.statusBar.drawCharPickerButton.hide()
        if self.appState.playOnlyMode:
            self.statusBar.hide()
            self.cursorOff()
        self.playing = True
        self.metaKey = 0
        if self.appState.playOnlyMode: 
            self.appState.drawBorders = False
        if not self.appState.playOnlyMode:
            # mode, show extra stuff.
            self.drawStatusBar()
        playedTimes = 1
        new_time = time.time()
        # see how many milliseconds we have to sleep for
        # then divide by 1000.0 since time.sleep() uses seconds
        sleep_time = (1000.0 / self.opts.framerate) / 1000.0
        self.mov.gotoFrame(self.appState.playbackRange[0])
        mouseX, mouseY = 0, 0
        while self.playing:
            # catch keyboard input - to change framerate or stop playing animation
            # get keyboard input, returns -1 if none available
            self.move(self.xy[0], self.xy[1])
            self.refresh()
            if not self.appState.playOnlyMode:
                self.drawStatusBar()
                self.move(self.xy[0], self.xy[1] - 1)   # reposition cursor
            c = self.stdscr.getch()
            if c == 27:
                self.metaKey = 1
                self.commandMode = True
                c = self.stdscr.getch() # normal esc
            if self.metaKey == 1 and not self.appState.playOnlyMode and c != curses.ERR:   # esc
                if c == 91: c = self.stdscr.getch() # alt-arrow does this in this mrxvt 5.x build
                if c in [61, 43]: # esc-= and esc-+ - fps up
                    self.increaseFPS()
                    sleep_time = (1000.0 / self.opts.framerate) / 1000.0
                elif c in [45]: # esc-- (alt minus) - fps down
                    self.decreaseFPS()
                    sleep_time = (1000.0 / self.opts.framerate) / 1000.0
                elif c in [98, curses.KEY_LEFT]:      # alt-left - prev bg color
                    self.prevBgColor()
                    c = None 
                elif c in [102, curses.KEY_RIGHT]:     # alt-right - next bg color
                    self.nextBgColor()
                    c = None 
                elif c in [curses.KEY_DOWN, "\x1b\x1b\x5b\x42"]:      # alt-down - prev fg color
                    self.prevFgColor()
                    c = None 
                elif c == curses.KEY_UP:     # alt-up - next fg color
                    self.nextFgColor()
                    c = None 
                elif c == 91 or c == 339:   # alt-[ previous character set. apparently this doesn't work
                    self.prevCharSet() # during playback, c == -1, so 339 is alt-pgup, as a backup
                elif c == 93 or c == 338:   # alt-] (93) or aplt-pagdown next character set
                    self.nextCharSet()
                elif c == 83:       # alt-S - pick a character set
                    self.showCharSetPicker()
                elif c == 46:       # alt-. - insert column
                    self.addCol(frange=self.appState.playbackRange)
                elif c == 44:      # alt-, - erase/pop current column
                    self.delCol(frange=self.appState.playbackRange)
                elif c == 47:      # alt-/ - insert line
                    self.addLine(frange=self.appState.playbackRange)
                elif c == 39:        # alt-' - erase line
                    self.delLine(frange=self.appState.playbackRange)
                elif c == 109 or c == 102:    # alt-m or alt-f - load menu
                    #self.statusBar.menuButton.on_click() 
                    self.openMenu("File")
                elif c == 99:     # alt-c - color picker
                    if self.appState.colorMode == "256":
                        self.statusBar.colorPickerButton.on_click()
                elif c == 122:  # alt-z = undo
                    self.undo.undo()
                    self.hardRefresh()
                elif c == 114:  # alt-r = redo
                    self.undo.redo()
                elif c == 82:   # alt-R = set playback range
                    self.getPlaybackRange()
                elif c in [112]: # alt-p - stop playing
                    self.stopPlaying()
                elif c == 111:                # alt-o - open
                    self.stopPlaying()
                    load_filename = self.openFilePicker()
                    if load_filename:   # if not False
                        self.clearCanvas(prompting=False)
                        self.loadFromFile(load_filename, 'dur')
                        self.move_cursor_topleft()
                elif c in [104, 63]:                # alt-h - help
                    self.showHelp()
                    c = None
                elif c == 113:                 # alt-q - quit
                    self.safeQuit()
                    self.stdscr.nodelay(1)
                    c = None
                else:
                    if self.appState.debug:
                        self.notify("keystroke: %d" % c) # alt-unknown
                self.commandMode = 0
                self.metaKey = 0
                c = None 
            elif c != -1:   # -1 means no keys are pressed.
                # up or down to change framerate, otherwise stop playing
                if self.appState.playOnlyMode:  # quit on any keystroke
                    self.playing = False
                else:
                    if c == curses.KEY_MOUSE: # Remember, we are playing here
                        try:
                            _, mouseX, mouseY, _, mouseState = curses.getmouse()
                        except:
                            pass
                        realmaxY,realmaxX = self.realstdscr.getmaxyx()
                        # enable mouse tracking only when the button is pressed
                        if mouseState == curses.BUTTON1_CLICKED:
                            if self.pressingButton:
                                self.pressingButton = False
                            
                        if mouseState & curses.BUTTON1_PRESSED:
                            if mouseY < self.mov.sizeY and mouseX < self.mov.sizeX: # in edit area
                                if not self.pressingButton:
                                    self.pressingButton = True
                                    print('\033[?1003h') # enable mouse tracking with the XTERM APIP
                            else:
                                self.pressingButton = False
                        else:
                            if self.pressingButton:
                                self.pressingButton = False
                                print('\033[?1003l') # disable mouse reporting
                                curses.mousemask(1)
                                curses.mousemask(curses.REPORT_MOUSE_POSITION | curses.ALL_MOUSE_EVENTS)
                        if self.pressingButton or mouseState == curses.BUTTON1_CLICKED:    # self.playing == True
                            self.gui.got_click("Click", mouseX, mouseY)
                            if mouseY < self.mov.sizeY and mouseX < self.mov.sizeX: 
                                # we clicked in edit area, so move the cursor
                                self.xy[1] = mouseX + 1 # set cursor position
                                self.xy[0] = mouseY + self.appState.topLine
                            elif mouseX < realmaxX and mouseY in [self.statusBarLineNum, self.statusBarLineNum+1]:   # we clicked on the status bar while playing.
                                if mouseY == self.statusBarLineNum: # clicked upper bar
                                    offset = 6  # making room for the menu bar
                                    tOffset = realmaxX - (realmaxX - self.transportOffset) + 6
                                    if mouseX in [tOffset, tOffset + 1]:  # clicked pause button
                                        self.clickHighlight(tOffset, "||")
                                        self.stopPlaying()
                                    elif mouseX == 12 + offset:    # clicked FPS down
                                        self.clickHighlight(12 + offset, "<")
                                        self.decreaseFPS()
                                        sleep_time = (1000.0 / self.opts.framerate) / 1000.0
                                    elif mouseX == 16 + offset:    # clicked FPS up
                                        self.clickHighlight(16 + offset, ">")
                                        self.increaseFPS()
                                        sleep_time = (1000.0 / self.opts.framerate) / 1000.0
                                elif mouseY == self.statusBarLineNum+1:    # clicked bottom bar
                                    if mouseX in range(4,20): 
                                        fg = mouseX - 3  
                                        self.setFgColor(fg)
                                    elif mouseX in range(25,33):    
                                        bg = mouseX - 24
                                        self.setBgColor(bg)
                                    elif mouseX == 66:  # clicked next character set
                                        self.clickHighlight(66, ">", bar='bottom')
                                        self.nextCharSet()
                                    elif mouseX == 34:  # clicked previous character set
                                        self.clickHighlight(34, "<", bar='bottom')
                                        self.prevCharSet()
                                    elif self.appState.debug:
                                        self.notify("bottom bar. " + str([mouseX, mouseY]))
                                elif self.appState.debug:
                                    self.notify("clicked. " + str([mouseX, mouseY]))

                    elif c == curses.KEY_LEFT:      # left - move cursor right a character
                        self.move_cursor_left()
                    elif c == curses.KEY_RIGHT:     # right - move cursor right
                        self.move_cursor_right()
                    elif c == curses.KEY_UP:    # up - move cursor up
                        self.move_cursor_up()
                    elif c == curses.KEY_DOWN:  # down - move curosr down
                        self.move_cursor_down()
                    elif c in [339, curses.KEY_PPAGE]:  # page up
                        self.move_cursor_pgup()
                    elif c in [338, curses.KEY_NPAGE]:  # page down
                        self.move_cursor_pgdown()
                    elif c in [339, curses.KEY_HOME]:  # 339 = home
                        self.xy[1] = 1
                    elif c in [338, curses.KEY_END]:   # 338 = end
                        self.xy[1] = self.mov.sizeX
                    elif c in [10, 13, curses.KEY_ENTER]:               # enter (10 if we
                        self.move_cursor_enter()
                        # don't do curses.nonl())
                    elif c in [263, 127]:              # backspace
                        self.backspace()
                    elif c in [330]:              # delete
                        self.deleteKeyPop(frange=self.appState.playbackRange)
                    elif c in [1, curses.KEY_HOME]:     # ctrl-a or home
                        self.xy[1] = 1
                    elif c in [5, curses.KEY_END]:      # ctrl-e or end
                        self.xy[1] = self.mov.sizeX
                    elif c in [curses.KEY_F1]:    # F1 - insert extended character
                        self.insertChar(self.chMap['f1'], fg=self.colorfg, bg=self.colorbg,
                                frange=self.appState.playbackRange)
                        c = None
                    elif c in [curses.KEY_F2]:    # F2 - insert extended character
                        self.insertChar(self.chMap['f2'], fg=self.colorfg, bg=self.colorbg,
                                frange=self.appState.playbackRange)
                        c = None
                    elif c in [curses.KEY_F3]:    # F3 - insert extended character
                        self.insertChar(self.chMap['f3'], fg=self.colorfg, bg=self.colorbg,
                                frange=self.appState.playbackRange)
                        c = None
                    elif c in [curses.KEY_F4]:    # F4 - insert extended character
                        self.insertChar(self.chMap['f4'], fg=self.colorfg, bg=self.colorbg,
                                frange=self.appState.playbackRange)
                        c = None
                    elif c in [curses.KEY_F5]:    # F5 - insert extended character
                        self.insertChar(self.chMap['f5'], fg=self.colorfg, bg=self.colorbg,
                                frange=self.appState.playbackRange)
                        c = None
                    elif c in [curses.KEY_F6]:    # F6 - insert extended character
                        self.insertChar(self.chMap['f6'], fg=self.colorfg, bg=self.colorbg,
                                frange=self.appState.playbackRange)
                        c = None
                    elif c in [curses.KEY_F7]:    # F7 - insert extended character
                        self.insertChar(self.chMap['f7'], fg=self.colorfg, bg=self.colorbg,
                                frange=self.appState.playbackRange)
                        c = None
                    elif c in [curses.KEY_F8]:    # F8 - insert extended character
                        self.insertChar(self.chMap['f8'], fg=self.colorfg, bg=self.colorbg,
                                frange=self.appState.playbackRange)
                        c = None
                    elif c in [curses.KEY_F9]:    # F9 - insert extended character
                        self.insertChar(self.chMap['f9'], fg=self.colorfg, bg=self.colorbg,
                                frange=self.appState.playbackRange)
                        c = None
                    elif c in [curses.KEY_F10]:    # F10 - insert extended character
                        self.insertChar(self.chMap['f10'], fg=self.colorfg, bg=self.colorbg,
                                frange=self.appState.playbackRange)
                        c = None
                    elif c <= 128 and c >= 32:      # normal printable character
                        self.insertChar(c, fg=self.colorfg, bg=self.colorbg, frange=self.appState.playbackRange)

            new_time = time.time()
            frame_delay = self.mov.currentFrame.delay
            if frame_delay > 0:
                realDelayTime = frame_delay
            else:
                realDelayTime = sleep_time
            if new_time >= (last_time + realDelayTime): # Time to update the frame? If so...
                last_time = new_time
                # draw animation
                if self.mov.currentFrameNumber == self.appState.playbackRange[1]:
                    self.mov.gotoFrame(self.appState.playbackRange[0])
                else:
                    self.mov.nextFrame()
                if not self.appState.playOnlyMode: # if we're not in play-only
                    # mode, show extra stuff.
                    self.drawStatusBar()
                else:
                    if self.appState.playNumberOfTimes > 0:   # if we're playing x times
                        if self.mov.currentFrameNumber == self.mov.frameCount:
                            # and on the last frame
                            if playedTimes < self.appState.playNumberOfTimes:
                                playedTimes += 1
                            else:   # we've played the desired number of times.
                                self.playing = False
                #self.refresh()
            else: time.sleep(0.005) # to keep from sucking up cpu
        self.stdscr.nodelay(0) # back to wait for input when calling getch
        self.cursorOn()

    def stopPlaying(self):
        self.playing = False
        self.statusBar.toolButton.show()
        if self.appState.cursorMode == "Draw":
            self.statusBar.drawCharPickerButton.show()

    def genCharSet(self, firstChar):   # firstChar is a unicode number
        newSet = {}
        newChar = firstChar
        for x in range(1,11):   # 1-10
            keyStr = 'f%i' % x
            newSet.update({keyStr:newChar})
            newChar += 1
        return newSet
            
    
    def initCharSet(self): # we can have nextCharSet and PrevCharSet to switch between chars in set
        # Can also add encoding= paramater for different encodings, eg: ascii, utf-8, etc.
        self.charMapNumber = 0
        if self.appState.characterSet == "Durdraw Default":
            self.fullCharMap = [ \
                # All of our unicode templates live here. Blank template:
                #{'f1':, 'f2':, 'f3':, 'f4':, 'f5':, 'f6':, 'f7':, 'f8':, 'f9':, 'f10':},

                # block characters
                {'f1':9617, 'f2':9618, 'f3':9619, 'f4':9608, 'f5':9600, 'f6':9604, 'f7':9612, 'f8':9616, 'f9':9632, 'f10':183 },    # ibm-pc looking block characters (but unicode instead of ascii)
                {'f1':9601, 'f2':9602, 'f3':9603, 'f4':9604, 'f5':9605, 'f6':9606, 'f7': 9607, 'f8':9608, 'f9'     :9600, 'f10':0x2594 },   # more block elements - mostly bottom half fills
                {'f1':0x2588, 'f2':0x2589, 'f3':0x258A, 'f4':0x258B, 'f5':0x258C, 'f6':0x258D, 'f7':0x258E, 'f8':0x258F, 'f9':0x2590, 'f10':0x2595},    # partial left and right fills

                # geometric shapes
                #{'f1':0x25dc, 'f2':0x25dd, 'f3':0x25de, 'f4':0x25df, 'f5':0x25e0, 'f6':0x25e1, 'f7':0x25e2, 'f8':0x25e3, 'f9':0x25e4, 'f10':0x25e5},    # little curves and triangles
                {'f1':0x25e2, 'f2':0x25e3, 'f3':0x25e5, 'f4':0x25e4, 'f5':0x25c4, 'f6':0x25ba, 'f7':0x25b2, 'f8':0x25bc, 'f9':0x25c0, 'f10':0x25b6 },    # little curves and triangles

                # terminal graphic characters
                {'f1':9622, 'f2':9623, 'f3':9624, 'f4':9625, 'f5':9626, 'f6':9627, 'f7':9628, 'f8':9629, 'f9':9630, 'f10':9631 },   # terminal graphic characters
                #{'f1':0x1FB9C, 'f2':0x1FB9D, 'f3':0x1FB9F, 'f4':0x1FB9E, 'f5':0x1FB9A, 'f6':0x1FB9B, 'f7':0x1FB65, 'f8':0x1FB5A, 'f9':0x1FB4B, 'f10':0x1FB40},  # legacy computing smooth terminal mosaic characters - newer versions of unicode Triangles and shit.. not sure why it isn't working
                #{'f1':9581, 'f2':9582, 'f3':9583, 'f4':9584, 'f5':9585, 'f6':9586, 'f7':9587, 'f8':9472, 'f9':9474, 'f10':9532 },   # character cell arcs, aka curved pipes
                {'f1':9581, 'f2':9582, 'f3':9584, 'f4':9583, 'f5':9472, 'f6':9474, 'f7':9585, 'f8':9586, 'f9':9587, 'f10':9532 },   # character cell arcs, aka curved pipes
                #{'f1':130032, 'f2':0x1FBF2, 'f3':0x1FBF3, 'f4':0x1FBF4, 'f5':0x1FBF5, 'f6':0x1FBF6, 'f7':0x1FBF7, 'f8':0x1FBF8, 'f9':0x1FBF9, 'f10':0x1FBF0},   # lcd/led-style digits
                #{'f1':0x1FB8C, 'f2':ord('🭀'), 'f3':0x1FBF3, 'f4':0x1FBF4, 'f5':0x1FBF5, 'f6':0x1FBF6, 'f7':0x1FBF7, 'f8':0x1FBF8, 'f9':0x1FBF9, 'f10':0x1FBF0},   # lcd/led-style digits
                ]
            # generate some unicode sets via offset
            self.fullCharMap.append(self.genCharSet(0x25a0)) # geometric shapes
            self.fullCharMap.append(self.genCharSet(0x25e6)) # more geometric shapes
            self.fullCharMap.append(self.genCharSet(0x25c6)) # geometrics - diamond and circles
            self.fullCharMap.append(self.genCharSet(0x02ef)) # UPA modifiers
            self.fullCharMap.append(self.genCharSet(0x02c2)) # UPA modifiers
            self.fullCharMap.append(self.genCharSet(0x2669)) # music symbols
            self.fullCharMap.append(self.genCharSet(0xFF66)) # half-width kanji letters
            self.fullCharMap.append(self.genCharSet(0xFF70)) # half-width kanji letters
            self.fullCharMap.append(self.genCharSet(0xFF7a)) # half-width kanji letters
            self.fullCharMap.append(self.genCharSet(0xFF84)) # half-width kanji letters
            self.fullCharMap.append(self.genCharSet(0xFF8e)) # half-width kanji letters
            #self.fullCharMap.append(self.genCharSet(0xFF98)) # half-width kanji letters
            #self.fullCharMap.append(self.genCharSet(0x1F603)) # smiley emojis
            self.fullCharMap.append(self.genCharSet(0x2801)) # braile a-j
            self.fullCharMap.append(self.genCharSet(0x2805)) # braile k-t
            self.fullCharMap.append(self.genCharSet(0x2825)) # braile u+
            self.fullCharMap.append(self.genCharSet(0x2b2c)) # ellipses
            self.chMap = self.fullCharMap[self.charMapNumber]

            # Map a dict of F1-f10 to character values 
            if self.appState.charEncoding == 'ibm-pc':
                self.chMap = {'f1':176, 'f2':177, 'f3':178, 'f4':219, 'f5':223, 'f6':220, 'f7':221, 'f8':222, 'f9':254, 'f10':250 }
                self.fullCharMap = [ self.chMap ]
                self.appState.colorPickChar = chr(219)  # ibm-pc/cp437 ansi block character
        elif self.appState.characterSet == "Unicode Block":
            self.setUnicodeBlock(block=self.appState.unicodeBlock)
            self.chMap = self.fullCharMap[self.charMapNumber]
        self.refreshCharMap()

    def setCharacterSet(self, set_name):
        """ Set a Durdraw character set (not a Unicode block name) """
        self.appState.characterSet = set_name
        miniSetName = f"{self.appState.characterSet[:3]}.."
        self.statusBar.charSetButton.label = miniSetName  # [Name..]

    def setUnicodeBlock(self, block="Symbols for Legacy Computing"):
        self.fullCharMap = durchar.load_unicode_block(block)
        self.chMap = self.fullCharMap[self.charMapNumber]
        if self.statusBar:
            if self.appState.characterSet == "Unicode Block":
                miniSetName = f"{self.appState.unicodeBlock[:3]}.."
            else:
                miniSetName = f"{self.appState.characterSet[:3]}.."
            self.statusBar.charSetButton.label = miniSetName  # [Name..]
        self.refreshCharMap()
        #self.chMapString = "F1%cF2%cF3%cF4%cF5%cF6%cF7%cF8%cF9%cF10%c" % \
        #self.chMapString = "F1%c F2%c F3%c F4%c F5%c F6%c F7%c F8%c F9%c F10%c " % \
        #        (self.chMap['f1'], self.chMap['f2'], self.chMap['f3'], self.chMap['f4'], self.chMap['f5'], \
        #        self.chMap['f6'], self.chMap['f7'], self.chMap['f8'], self.chMap['f9'], self.chMap['f10'] )

    def nextCharSet(self):
        if self.charMapNumber == len(self.fullCharMap) - 1:
            self.charMapNumber = 0
        else:
            self.charMapNumber += 1
        self.refreshCharMap()

    def prevCharSet(self):
        if self.charMapNumber == 0:
            self.charMapNumber = len(self.fullCharMap) - 1
        else:
            self.charMapNumber -= 1
        self.refreshCharMap()

    def refreshCharMap(self):
        # checks self.charMapNumber and does the rest
        self.chMap = self.fullCharMap[self.charMapNumber]
        #self.chMapString = "F1%c F2%c F3%c F4%c F5%c F6%c F7%c F8%c F9%c F10%c " % \
        self.chMapString = "F1%cF2%cF3%cF4%cF5%cF6%cF7%cF8%cF9%cF10%c" % \
                (self.chMap['f1'], self.chMap['f2'], self.chMap['f3'], self.chMap['f4'], self.chMap['f5'], \
                self.chMap['f6'], self.chMap['f7'], self.chMap['f8'], self.chMap['f9'], self.chMap['f10'] )

    def clearStatusLine(self):
        # fyi .. width and height in this context should go into
        # appState, not in Movie(). In other words, this == not
        # the width and height of the movie, but of the editor screen.
        realmaxY,realmaxX = self.realstdscr.getmaxyx()
        self.addstr(self.statusBarLineNum, 0, " " * realmaxX)
        self.addstr(self.statusBarLineNum+1, 0, " " * realmaxX)

    def resizeHandler(self):
        """ Called when the window is resized """
        # stick bottom of drawing to the bottom of the window
        # when resizing
        topLine = self.mov.sizeY - self.realmaxY - 2
        if topLine < 0:
            topLine = 0
        self.appState.topLine = topLine
        if self.xy[0] < self.appState.topLine:   # if cursor is off screen
            self.xy[0] = self.appState.topLine   # put it back on
        pass

    def drawStatusBar(self):
        if self.statusBar.hidden:
            return False
        mainColor = self.appState.theme['mainColor']
        clickColor = self.appState.theme['clickColor']
        
        # This has also become a bit of a window resize handler
        if not self.playing:
            self.clearStatusLine()
        else:
            #self.clearStatusBarNoRefresh()
            pass
        self.line_1_offset = 5
        line_1_offset = self.line_1_offset
        realmaxY,realmaxX = self.realstdscr.getmaxyx()
        statusBarLineNum = realmaxY - 2
        self.statusBar.colorPicker.handler.move(0,realmaxY - 6)
        self.statusBarLineNum = statusBarLineNum
        # resize window, tell the statusbar buttons
        self.statusBar.menuButton.update_real_xy(x = statusBarLineNum)
        self.statusBar.toolButton.update_real_xy(x = statusBarLineNum)
        self.statusBar.charSetButton.update_real_xy(x = statusBarLineNum + 1)
        self.statusBar.drawCharPickerButton.update_real_xy(x = statusBarLineNum)
        if self.appState.colorMode == "256":
            self.statusBar.colorPickerButton.update_real_xy(x = statusBarLineNum + 1)
        canvasSizeBar = f"[{self.mov.sizeX}x{self.mov.sizeY}]"
        canvasSizeOffset = realmaxX - len(canvasSizeBar) - 1     # right of transport
        self.addstr(statusBarLineNum, canvasSizeOffset, canvasSizeBar, curses.color_pair(mainColor))
        frameBar = "F: %i/%i " % (self.mov.currentFrameNumber, self.mov.frameCount)
        rangeBar = "R: %i/%i " % (self.appState.playbackRange[0], self.appState.playbackRange[1])
        fpsBar = "<FPS>: %i " % (self.opts.framerate)
        delayBar = "D: %.2f " % (self.mov.currentFrame.delay)
        self.addstr(statusBarLineNum, 2 + line_1_offset, frameBar, curses.color_pair(mainColor))
        self.addstr(statusBarLineNum, 12 + line_1_offset, fpsBar, curses.color_pair(mainColor))
        self.addstr(statusBarLineNum, 23 + line_1_offset, delayBar, curses.color_pair(mainColor))
        self.addstr(statusBarLineNum, 31 + line_1_offset, rangeBar, curses.color_pair(mainColor))

        if self.appState.debug:
            cp = self.ansi.colorPairMap[(self.colorfg, self.colorbg)]
            cp2 = self.colorpair
            pairs = len(self.ansi.colorPairMap) 
            try:
                extColors = curses.has_extended_color_support()
            except:
                extColors = False
            colorValue = curses.color_content(self.colorfg)
            debugstring = f"Fg: {self.colorfg}, bg: {self.colorbg}, cpairs: {cp}, {cp2}, pairs: {pairs}, ext: {extColors}, {colorValue}"
            self.addstr(statusBarLineNum-1, 0, debugstring, curses.color_pair(mainColor))
        # Draw FG and BG colors
        if self.appState.colorMode == "256":
            self.addstr(statusBarLineNum+1, 0, "FG:", curses.color_pair(clickColor) | curses.A_BOLD)
            cp = self.ansi.colorPairMap[(self.colorfg, 0)]
            self.addstr(statusBarLineNum+1, 3, self.appState.colorPickChar * 2, curses.color_pair(cp))
        if self.appState.showBgColorPicker:
            self.addstr(statusBarLineNum+1, 6, "BG:", curses.color_pair(clickColor) | curses.A_BOLD)
            cp = self.ansi.colorPairMap[(1, self.colorbg)]
            fillChar = ' '
            self.addstr(statusBarLineNum+1, 9, fillChar * 2, curses.color_pair(cp))

        # Draw character map for f1-f10 (block characters)
        chMapOffset = 35    # how far in to show the character map
        self.addstr(statusBarLineNum+1, chMapOffset-1, "<", curses.color_pair(clickColor) | curses.A_BOLD)
        self.addstr(statusBarLineNum+1, 66, ">", curses.color_pair(clickColor) | curses.A_BOLD)
        if self.colorfg > 8 and self.appState.colorMode == "16":    # bright color
            self.addstr(statusBarLineNum+1, chMapOffset, self.chMapString, curses.color_pair(self.colorpair) | curses.A_BOLD)
        else:   # normal color
            self.addstr(statusBarLineNum+1, chMapOffset, self.chMapString, curses.color_pair(self.colorpair))
        # draw current character set #
        charSetNumberString = f"({self.charMapNumber+1}/{len(self.fullCharMap)})"
        #self.addstr(statusBarLineNum+1, chMapOffset+len(self.chMapString)+2, charSetNumberString, curses.color_pair(mainColor)) 
        if self.appState.colorMode == "16":   # put it to the right instead of the left, to make room for BG colors
            self.addstr(statusBarLineNum+1, chMapOffset+len(self.chMapString)+2, charSetNumberString, curses.color_pair(mainColor)) 
        #if self.appState.colorMode == 256:
        else:
            self.addstr(statusBarLineNum+1, chMapOffset-16, charSetNumberString, curses.color_pair(mainColor)) 
        #self.addstr(statusBarLineNum+1, chMapOffset+len(self.chMapString)+2, str(self.charMapNumber+1), curses.color_pair(mainColor)) 
        # overlay draw function key names in normal color
        y = 0
        #for x in range(1,11): 
        #    self.addstr(statusBarLineNum+1, chMapOffset+y, "F%i" % x, curses.color_pair(mainColor))
        #    y = y + 3

        # draw 16-color picker
        if self.appState.colorMode == "16":
            colorPickerFGOffset = 0
            self.addstr(statusBarLineNum+1, colorPickerFGOffset, "FG:", curses.color_pair(mainColor))
            for c in range(1,17):
                cp = self.ansi.colorPairMap[(c, 0)]
                if c > 8:
                    if c == self.colorfg:
                        self.addstr(statusBarLineNum+1, colorPickerFGOffset+2+c,'X', curses.color_pair(cp) | curses.A_BOLD)   # block character
                    else:
                        self.addstr(statusBarLineNum+1, colorPickerFGOffset+2+c, self.appState.colorPickChar, curses.color_pair(cp) | curses.A_BOLD)   # block character
                else:
                    if c == self.colorfg:
                        if c == 1: # black fg
                            self.addstr(statusBarLineNum+1, colorPickerFGOffset+2+c,'X', curses.color_pair(mainColor))
                        else:
                            self.addstr(statusBarLineNum+1, colorPickerFGOffset+2+c,'X', curses.color_pair(cp))   # block character
                    else:
                        self.addstr(statusBarLineNum+1, colorPickerFGOffset+2+c, self.appState.colorPickChar, curses.color_pair(cp))
            # bg color
            colorPickerBGOffset = 21
            self.addstr(statusBarLineNum+1, colorPickerBGOffset, "BG:", curses.color_pair(mainColor))
            for c in range(1,9):
                cp = self.ansi.colorPairMap[(c, 0)]
                if c == self.colorbg: #or (c == 8 and self.colorbg == 0):
                    #self.addstr(statusBarLineNum+1, colorPickerBGOffset+3+c, 'X', curses.color_pair(self.ansi.colorPairMap[(16, c)])) 
                    if c == 9: # black bg
                        self.addstr(statusBarLineNum+1, colorPickerBGOffset+3+c, 'X', curses.color_pair(mainColor)) 
                    else:
                        self.addstr(statusBarLineNum+1, colorPickerBGOffset+3+c, 'X', curses.color_pair(self.ansi.colorPairMap[(16, c)])) 
                else:
                    self.addstr(statusBarLineNum+1, colorPickerBGOffset+3+c, self.appState.colorPickChar, curses.color_pair(cp + 1))
        # Draw x/y location/position 
        locationString = "(%i,%i)" % (self.xy[1]-1, self.xy[0])
        locationStringOffset = realmaxX - len(locationString) - 1
        self.addstr(statusBarLineNum+1, locationStringOffset, locationString, curses.color_pair(mainColor))
        # Draw Range, FPS and Delay buttons
        self.addstr(statusBarLineNum, 12 + line_1_offset, "<", curses.color_pair(clickColor) | curses.A_BOLD)  # FPS buttons
        self.addstr(statusBarLineNum, 16 + line_1_offset, ">", curses.color_pair(clickColor) | curses.A_BOLD)
        if self.commandMode:
            self.addstr(statusBarLineNum, realmaxX - 1, "*", curses.color_pair(2) | curses.A_BOLD)
        else:
            self.addstr(statusBarLineNum, realmaxX - 1, " ", curses.color_pair(2) | curses.A_BOLD)
        if self.appState.modified:
            self.addstr(statusBarLineNum + 1, realmaxX - 1, "*", curses.color_pair(4) | curses.A_BOLD)
        else:
            self.addstr(statusBarLineNum + 1, realmaxX - 1, " ", curses.color_pair(4) | curses.A_BOLD)
        if not self.playing:
            self.addstr(statusBarLineNum, 2 + line_1_offset, "F", curses.color_pair(clickColor) | curses.A_BOLD)  # Frame button
            self.addstr(statusBarLineNum, 31 + line_1_offset, "R", curses.color_pair(clickColor) | curses.A_BOLD)  # Range button
            self.addstr(statusBarLineNum, 23 + line_1_offset, "D", curses.color_pair(clickColor) | curses.A_BOLD)  # Delay button
        # draw transport
        transportString = "|< << |> >> >|" 
        transportOffset = realmaxX - len(transportString) - 11
        self.transportOffset = transportOffset
        if self.playing:
            transportString = "|< << || >> >|" 
            self.addstr(statusBarLineNum, transportOffset, transportString, curses.color_pair(mainColor))
            self.addstr(statusBarLineNum, transportOffset+6, "||", curses.color_pair(clickColor) | curses.A_BOLD)
        else:
            transportString = "|< << |> >> >|" 
            self.addstr(statusBarLineNum, transportOffset, transportString, curses.color_pair(clickColor) | curses.A_BOLD)
        # Draw the new status bar
        self.statusBar.draw()
        # if cursor is outside of canvas, fix it
        bottomLine = self.realmaxY - 3 + self.appState.topLine
        if self.xy[0] > self.mov.sizeY - 1:  # cursor is past bottom of the canvas
            self.xy[0] = self.mov.sizeY - 1
        if self.xy[1] > self.opts.sizeX:    # cursor is past right edge of the canvas
            self.xy[1] = self.opts.sizeX
        # if it's off screen.. fix that, too
        if self.xy[0] - self.appState.topLine > realmaxY - 3:
            self.xy[0] = realmaxY - 3 + self.appState.topLine
        if self.xy[1] < 0:
            self.xy[1] = 1
        self.move(self.xy[0], self.xy[1] - 1)

    def clickHighlight(self, pos, buttonString, bar='top'):    # Visual feedback
        # example: self.clickHighlight(52, "|>")
        # Highlight clicked item at "pos" by drawing it as "str" in bright white or yellow, sleep a moment,
        # then back to green
        if bar == 'top':
            y = self.statusBarLineNum
        if bar == 'bottom':
            y = self.statusBarLineNum + 1
        self.addstr(y, pos, buttonString, curses.color_pair(self.appState.theme['clickHighlightColor']) | curses.A_BOLD)
        curses.curs_set(0)  # turn off cursor
        self.stdscr.refresh()
        time.sleep(0.2)
        self.addstr(y, pos, buttonString, curses.color_pair(self.appState.theme['clickColor']))
        curses.curs_set(1)  # turn on cursor


    def mainLoop(self):
        self.metaKey = 0
        self.commandMode = False
        mouseX, mouseY = 0, 0
        self.pressingButton = False
        while 1:    # Real "main loop" - get user input, aka "edit mode"
            self.testWindowSize()
            # print statusbar stuff
            self.drawStatusBar()
            self.move(self.xy[0], self.xy[1] - 1)  # move cursor to the right
            # spot for refresh
            curses.panel.update_panels()
            self.stdscr.refresh()
            c = self.stdscr.getch()
            self.testWindowSize()
            if c in ["\x1b\x1b\x5b\x42"]: self.notify("alt-down")
            if self.metaKey == 1:
                if c == 111:                # alt-o - open
                    load_filename = self.openFilePicker()
                    if load_filename:   # if not False
                        self.clearCanvas(prompting=False)
                        self.loadFromFile(load_filename, 'dur')
                        self.move_cursor_topleft()
                elif c == 115:                 # alt-s - save
                    self.save()
                    c = None
                elif c == 113:                 # alt-q - quit
                    self.safeQuit()
                    c = None
                elif c in [104, 63]:                # alt-h - help
                    self.showHelp()
                    c = None
                #elif c in [98, curses.KEY_LEFT]:      # alt-left - prev bg color
                elif c in [curses.KEY_LEFT]:      # alt-left - prev bg color
                    self.prevBgColor()
                    c = None
                #elif c in [102, curses.KEY_RIGHT]:     # alt-right - next bg color
                elif c in [curses.KEY_RIGHT]:     # alt-right - next bg color
                    self.nextBgColor()
                    c = None
                elif c in [curses.KEY_DOWN, "\x1b\x1b\x5b\x42"]:      # alt-down - prev fg color
                    self.prevFgColor()
                    c = None
                elif c == curses.KEY_UP:     # alt-up - next fg color
                    self.nextFgColor()
                    c = None
                elif c == 91 or c == 339:   # alt-[ (91) or alt-pgup (339). previous character set
                    self.prevCharSet()
                elif c == 93 or c == 338:   # alt-] or alt-pgdown, next character set
                    self.nextCharSet()
                elif c == 83:       # alt-S - pick a character set or unicode block
                    self.showCharSetPicker()
                elif c == 44:      # alt-, - erase/pop current column in frame
                    self.delCol()
                elif c == 46:       # alt-. - insert column in frame
                    self.addCol()
                elif c == 62:       # alt-> - insert column in canvas
                    self.addColToCanvas()
                elif c == 60:       # alt-< - delete column from canvas
                    self.delColFromCanvas()
                elif c == 34:       # alt-" - insert line in canvas
                    self.addLineToCanvas()
                elif c == 58:        # alt-: - erase line from canvas
                    self.delLineFromCanvas()
                elif c == 47:      # alt-/ - insert line
                    self.addLine()
                elif c == 39:        # alt-' - erase line
                    self.delLine()
                elif c ==121:       # alt-y - Eyedrop
                    self.eyeDrop(self.xy[1] - 1, self.xy[0])    # cursor position
                elif c == 109 or c == 102:    # alt-m or alt-f - load menu
                    self.openMenu("File")
                    #self.statusBar.menuButton.on_click() 
                elif c == 116: # or c =- 84:    # alt-t or alt-T - mouse tools menu
                    self.openMenu("Mouse Tools")
                    #self.statusBar.toolButton.on_click() 
                elif c == 99:     # alt-c - color picker
                    if self.appState.colorMode == "256":
                        self.statusBar.colorPickerButton.on_click()
                # Animation Keystrokes
                elif c == 68:     #alt-D - set delay for current frame
                    self.getDelayValue()
                elif c == 107:          # alt-k - next frame
                    self.mov.nextFrame()
                    self.refresh()  
                elif c == 106:          # alt-j or alt-j - previous frame
                    self.mov.prevFrame()
                    self.refresh()
                elif c == 103:            # alt-g - go to frame
                    self.gotoFrameGetInput()
                elif c == 67:             # alt-C - clear canvas/new
                    self.clearCanvas(prompting=True)
                elif c == 110 or c == 14:          # alt-n - clone to new frame
                    self.undo.push()
                    if self.mov.insertCloneFrame():
                        if self.appState.playbackRange[0] == 1 and \
                                self.appState.playbackRange[1] == self.mov.frameCount - 1:
                            self.appState.playbackRange = (self.appState.playbackRange[0], \
                                self.appState.playbackRange[1] + 1)
                    self.refresh()
                elif c == 78:          # alt-N (shift-alt-n) - new  empty frame
                    self.undo.push()
                    if self.mov.addEmptyFrame():
                        if self.appState.playbackRange[0] == 1 and \
                                self.appState.playbackRange[1] == self.mov.frameCount - 1:
                            self.appState.playbackRange = (self.appState.playbackRange[0], \
                                    self.appState.playbackRange[1] + 1)
                    self.refresh()
                elif c == 77:         # alt-M - move current frame
                    self.moveCurrentFrame()
                elif c == 100:      # alt-d - delete current frame
                    if self.deleteCurrentFramePrompt():
                        if self.appState.playbackRange[0] == 1 and \
                                self.appState.playbackRange[1] == self.mov.frameCount + 1:
                            self.appState.playbackRange = (self.appState.playbackRange[0], \
                                self.appState.playbackRange[1] - 1)
                    self.refresh()
                elif c == 122:  # alt-z = undo
                    self.undo.undo()
                    self.hardRefresh()
                elif c == 114:  # alt-r = redo
                    self.undo.redo()
                elif c == 118:  # alt-v      - paste
                    # Paste from the clipboard
                    if self.clipBoard:  # If there is something in the clipboard
                        self.pasteFromClipboard()
                elif c == 82:   # alt-R = set playback range
                    self.getPlaybackRange()
                elif c == 112:    # esc-p - start playing, any key exits
                    self.commandMode = False
                    self.metaKey = 0
                    self.startPlaying()
                elif c in [61, 43]: # esc-= and esc-+ - fps up
                    self.increaseFPS()
                elif c in [45]: # esc-- (alt minus) - fps down
                    self.decreaseFPS()
                elif c in [75]: # alt-K = start marking selection
                    startPoint=(self.xy[0] + self.appState.topLine, self.xy[1])
                    self.startSelecting(firstkey=c)  # start selecting text
                else:
                    if self.appState.debug: 
                        self.notify("keystroke: %d" % c) # alt-unknown
                self.commandMode = False
                self.metaKey = 0
                c = None
            # Meta key (alt) was not pressed, so look for non-meta chars
            if c == 27:
                self.metaKey = 1
                self.commandMode = True
                c = None
            if c == 24: self.safeQuit()     # ctrl-x
            elif c == 15:               # ctrl-o - open
                load_filename = self.openFilePicker()
                if load_filename:   # if not False
                    self.clearCanvas(prompting=False)
                    self.loadFromFile(load_filename, 'dur')
                    self.move_cursor_topleft()
                c = None
            elif c == 23:               # ctrl-w - save
                self.save()
                c = None
            elif c == 12:               # ctrl-l - harder refresh
                self.hardRefresh()
                c = None
            elif c in [10, 13, curses.KEY_ENTER]:               # enter (10 if we
                self.move_cursor_enter()
            elif c in [263, 127]:              # backspace
                self.backspace()
            elif c in [330]:              # delete
                self.deleteKeyPop()
            elif c in [339, curses.KEY_PPAGE]:  # page up
                self.move_cursor_pgup()
            elif c in [338, curses.KEY_NPAGE]:  # page down
                self.move_cursor_pgdown()
            elif c in [1, curses.KEY_HOME]:     # ctrl-a or home
                self.move_cursor_home()
            elif c in [5, curses.KEY_END]:      # ctrl-e or end
                self.move_cursor_end()
            elif c in [curses.KEY_F1]:    # F1 - insert extended character
                self.insertChar(self.chMap['f1'], fg=self.colorfg, bg=self.colorbg)
                c = None
            elif c in [curses.KEY_F2]:    # F2 - insert extended character
                self.insertChar(self.chMap['f2'], fg=self.colorfg, bg=self.colorbg)
                c = None
            elif c in [curses.KEY_F3]:    # F3 - insert extended character
                self.insertChar(self.chMap['f3'], fg=self.colorfg, bg=self.colorbg)
                c = None
            elif c in [curses.KEY_F4]:    # F4 - insert extended character
                self.insertChar(self.chMap['f4'], fg=self.colorfg, bg=self.colorbg)
                c = None
            elif c in [curses.KEY_F5]:    # F5 - insert extended character
                self.insertChar(self.chMap['f5'], fg=self.colorfg, bg=self.colorbg)
                c = None
            elif c in [curses.KEY_F6]:    # F6 - insert extended character
                self.insertChar(self.chMap['f6'], fg=self.colorfg, bg=self.colorbg)
                c = None
            elif c in [curses.KEY_F7]:    # F7 - insert extended character
                self.insertChar(self.chMap['f7'], fg=self.colorfg, bg=self.colorbg)
                c = None
            elif c in [curses.KEY_F8]:    # F8 - insert extended character
                self.insertChar(self.chMap['f8'], fg=self.colorfg, bg=self.colorbg)
                c = None
            elif c in [curses.KEY_F9]:    # F9 - insert extended character
                self.insertChar(self.chMap['f9'], fg=self.colorfg, bg=self.colorbg)
                c = None
            elif c in [curses.KEY_F10]:    # F10 - insert extended character
                self.insertChar(self.chMap['f10'], fg=self.colorfg, bg=self.colorbg)
                c = None
            elif c == curses.KEY_LEFT:      # left - move cursor right a character
                self.move_cursor_left()
            elif c == curses.KEY_RIGHT:     # right - move cursor right
                self.move_cursor_right()
            elif c == curses.KEY_UP:    # up - move cursor up
                self.move_cursor_up()
            elif c == curses.KEY_DOWN:  # down - move curosr down
                self.move_cursor_down()
            elif c in [339, curses.KEY_HOME]:  # 339 = home. not in xterm :'(
                self.move_cursor_home()
            elif c in [338, curses.KEY_END]:   # 338 = end
                self.move_cursor_end()
            elif c != curses.KEY_MOUSE and self.pressingButton:
                self.pressingButton = False
            elif c == curses.KEY_MOUSE: # We are not playing
                try:
                    _, mouseX, mouseY, _, mouseState = curses.getmouse()
                except:
                    pass
                if mouseY < self.mov.sizeY and mouseX < self.mov.sizeX: # we're in the canvas, not playing
                    if mouseState & curses.BUTTON1_PRESSED:
                        if not self.pressingButton:
                            self.pressingButton = True
                            print('\033[?1003h') # enable mouse tracking with the XTERM API
                        if not self.pushingToClip:
                            cmode = self.appState.cursorMode
                            if cmode == "Draw" or cmode == "Color" or cmode == "Erase":
                                self.undo.push()
                                self.pushingToClip = True
                    elif mouseState & curses.BUTTON1_RELEASED:
                        if self.pressingButton:
                            self.pressingButton = False
                            print('\033[?1003l') # disable mouse reporting
                            curses.mousemask(1)
                            curses.mousemask(curses.REPORT_MOUSE_POSITION | curses.ALL_MOUSE_EVENTS)
                            if self.pushingToClip:
                                self.pushingToClip = False
                            self.stdscr.redrawwin()
                    #elif mouseState & curses.BUTTON4_PRESSED:   # wheel up
                    #    self.move_cursor_down()
                    #elif mouseState & curses.BUTTON5_PRESSED:   # wheel down
                    #    self.move_cursor_down()
                    if self.appState.cursorMode == "Move":   # select mode/move the cursor
                        self.xy[1] = mouseX + 1     # set cursor position
                        self.xy[0] = mouseY + self.appState.topLine
                    elif self.appState.cursorMode == "Draw":   # Change the color under the cursor
                        # also set cursor position
                        self.xy[1] = mouseX + 1 # set cursor position
                        self.xy[0] = mouseY + self.appState.topLine
                        # Insert the selected character.
                        drawChar = self.appState.drawChar
                        self.insertChar(ord(drawChar), fg=self.colorfg, bg=self.colorbg, x=mouseX+1, y=mouseY + self.appState.topLine, moveCursor=False, pushUndo=False)
                        self.refresh()

                    elif self.appState.cursorMode == "Color":   # Change the color under the cursor
                        # also set cursor position
                        self.xy[1] = mouseX + 1 # set cursor position
                        self.xy[0] = mouseY + self.appState.topLine
                        self.insertColor(fg=self.colorfg, bg=self.colorbg, x=mouseX+1, y=mouseY + self.appState.topLine, pushUndo=False)
                        self.refresh()
                    elif self.appState.cursorMode == "Erase":   # Erase character under the cursor
                        # also set cursor position
                        self.xy[1] = mouseX + 1 # set cursor position
                        self.xy[0] = mouseY + self.appState.topLine
                        self.insertChar(ord(' '), fg=self.colorfg, bg=self.colorbg, x=mouseX, y=mouseY + self.appState.topLine, pushUndo=False)
                    elif self.appState.cursorMode == "Eyedrop":   # Change the color under the cursor
                        self.eyeDrop(mouseX, mouseY)
                    elif self.appState.cursorMode == "Select":   # Change the color under the cursor
                        self.xy[1] = mouseX + 1 # set cursor position
                        self.xy[0] = mouseY + self.appState.topLine
                        self.startSelecting(mouse=True)
                elif self.pressingButton:
                    self.pressingButton = False
                    print('\033[?1003l') # disable mouse reporting
                    curses.mousemask(1)
                    curses.mousemask(curses.REPORT_MOUSE_POSITION | curses.ALL_MOUSE_EVENTS)
                        #self.mov.currentFrame.newColorMap[self.xy[0]][self.xy[1] - 1] = [self.colorfg, self.colorbg]
                if mouseState == curses.BUTTON1_CLICKED:
                    realmaxY,realmaxX = self.realstdscr.getmaxyx()
                    self.gui.got_click("Click", mouseX, mouseY)
                    if mouseY < self.mov.sizeY and mouseX < self.mov.sizeX: # we're in the canvas
                        cmode = self.appState.cursorMode
                        if cmode == "Draw" or cmode == "Color" or cmode == "Erase":
                            self.undo.push()
                    if mouseX < realmaxX and mouseY in [self.statusBarLineNum, self.statusBarLineNum+1]:   # we clicked on the status bar somewhere..
                        # Add stuff here to take mouse 'commands' like clicking
                        # play/next/etc on transport, or clicking "start button"
                        if mouseY == self.statusBarLineNum: # clicked upper bar 
                            offset = self.line_1_offset # line 1 of the status bar 
                            tOffset = self.transportOffset
                            if mouseX in [tOffset + 6, tOffset + 7]:  # clicked play button
                                self.clickHighlight(tOffset + 6, "|>")
                                self.startPlaying()
                                self.metaKey = 0
                            elif mouseX in [tOffset + 3, tOffset + 4]: # goto prev frame
                                self.clickHighlight(tOffset + 3, "<<")
                                self.mov.prevFrame()
                            elif mouseX in [tOffset + 9, tOffset + 10]: # goto next frame
                                self.clickHighlight(tOffset + 9, ">>")
                                self.mov.nextFrame()
                            elif mouseX in [tOffset, tOffset + 1]: # goto first frame
                                self.clickHighlight(tOffset, "|<")
                                self.mov.gotoFrame(1)
                            elif mouseX in [tOffset + 12, tOffset + 13]: # goto last frame
                                self.clickHighlight(tOffset + 12, ">|")
                                self.mov.nextFrame()
                                self.mov.gotoFrame(self.mov.frameCount)
                            elif mouseX == 12 + offset:    # clicked FPS down
                                self.clickHighlight(12 + offset, "<")
                                self.decreaseFPS()
                            elif mouseX == 16 + offset:    # clicked FPS up
                                self.clickHighlight(16 + offset, ">")
                                self.increaseFPS()
                            elif mouseX == 23 + offset:  # clicked Delay button
                                self.clickHighlight(23 + offset, "D")
                                self.getDelayValue()
                            elif mouseX == 31 + offset:  # clicked Range button
                                self.clickHighlight(31 + offset, "R")
                                self.getPlaybackRange()
                            elif mouseX == 2 + offset:   # clicked Frame button
                                self.clickHighlight(2 + offset, "F")
                                self.gotoFrameGetInput()


                        elif mouseY == self.statusBarLineNum+1: # clicked bottom bar 
                            if self.appState.colorMode == "16":
                                if mouseX in range(3,19): # clicked a fg color
                                    fg = mouseX - 2
                                    self.setFgColor(fg)
                                elif mouseX in range(25,33):   # clicked a bg color
                                    bg = mouseX - 24
                                    self.setBgColor(bg)
                            if mouseX == 66:  # clicked next character set
                                self.clickHighlight(66, ">", bar='bottom')
                                self.nextCharSet()
                            elif mouseX == 34:  # clicked previous character set
                                self.clickHighlight(34, "<", bar='bottom')
                                self.prevCharSet()
                            elif self.appState.debug:
                                self.notify("bottom bar. " + str([mouseX, mouseY]))
                        else:
                            if self.appState.debug:
                                self.notify(str([mouseX, mouseY]))
            elif c in [curses.KEY_SLEFT, curses.KEY_SRIGHT, 337, 336, 520, 513]:
                # 337 and 520 - shift-up, 336 and 513 = shift-down
                # shift-up, shift-down, shift-left and shift-right = start selecting text block
                # shift-up and shift-down not defined in ncurses :(
                # doesn't seem to work in screen?
                startPoint=(self.xy[0] + self.appState.topLine, self.xy[1])
                self.startSelecting(firstkey=c)  # start selecting text
                # pass c to something here that starts selecting and moves
                # the cursor based on c, and knows whether it's selecting
                # via shift-arrow or mouse.
            elif c == None: pass
            elif c <= 128 and c >= 32:      # normal printable character
                self.insertChar(c, fg=self.colorfg, bg=self.colorbg)
            self.drawStatusBar()
            self.refresh()

    def move_cursor_enter(self):
        bottomLine = self.realmaxY - 3 + self.appState.topLine
        # move the cursor down
        if self.xy[0] < self.mov.sizeY:
            self.xy = [self.xy[0] + 1, 1]

    def move_cursor_pgup(self):
        # if we're at the top of the screen
        if self.xy[0] == 0: # already on first line
            if self.xy[1] > 0:  # not on first column..
                self.xy[1] = 1  # so go there
        # top of screen, but not top of file, go up a page
        elif self.xy[0] == self.appState.topLine:
            pageSize = self.realmaxY - 2
            self.xy[0] -= pageSize
            self.appState.topLine -= pageSize
            if self.xy[0] < 0:  # if we overflowed into negatives...
                self.xy[0] = 0
                self.appState.topLine = 0
        # not at top of screen at all, go to top of screen
        elif self.xy[0] > self.appState.topLine:
            self.xy[0] = self.appState.topLine

    def move_cursor_pgdown(self):
        bottomLine = self.realmaxY - 3 + self.appState.topLine
        if bottomLine > self.mov.sizeY:
            bottomLine = self.mov.sizeY - 1
        # We're already on the last line
        if self.xy[0] == self.mov.sizeY - 1:
            if self.xy[1] > 0:  # not on first column..
                self.xy[1] = 1  # so go there
        # bottom of screen, not bottom of file, go down a page
        elif self.xy[0] == bottomLine:
            pageSize = self.realmaxY - 2
            self.xy[0] += pageSize
            self.appState.topLine += pageSize
            if self.xy[0] > self.mov.sizeY - 1:  # if we overshot the end of the file..
                self.xy[0] = self.mov.sizeY - 1
                self.appState.topLine = self.mov.sizeY - pageSize
        # middle of screen, go to bottom
        elif self.xy[0] - self.appState.topLine < bottomLine:
            self.xy[0] = bottomLine

    def move_cursor_topleft(self):
        self.xy[0] = 0
        self.xy[1] = 1
        self.refresh()

    def move_cursor_left(self):     # pressed LEFT key
        if self.xy[1] > 1:
            self.xy[1] = self.xy[1] - 1

    def move_cursor_right(self):    # pressed RIGHT key
        if self.xy[1] < self.mov.sizeX:
            self.xy[1] = self.xy[1] + 1

    def move_cursor_up(self):   # pressed UP key
        if self.xy[0] > 0:
            self.xy[0] = self.xy[0] - 1
            if self.xy[0] - self.appState.topLine + 1 == 0 and self.appState.topLine > 0:  # if we're at the top of the screen
                self.appState.topLine -= 1   # scrolll up a line

    def move_cursor_down(self): # pressed DOWN key
        if self.xy[0] < self.mov.sizeY - 1:
            self.xy[0] = self.xy[0] + 1 # down a line
            if self.xy[0]  - self.appState.topLine > self.realmaxY - 3: # if we're at the bottom of the screen
                self.appState.topLine += 1  # scroll down a line

    def move_cursor_home(self):
        self.xy[1] = 1

    def move_cursor_end(self):
        self.xy[1] = self.mov.sizeX

    def getDelayValue(self):
        """ Ask the user for the delay value to set for current frame, then
            set it """
        self.clearStatusLine()
        self.promptPrint(f"Current frame delay == {self.mov.currentFrame.delay}, new value in seconds: ")
        curses.echo()
        try:
            delayValue = float(self.stdscr.getstr())
        except ValueError:
            delayValue = -1
        curses.noecho()
        self.clearStatusLine()
        if delayValue >= 0.0 and delayValue <= 120.0: # hard limit of 0 to 120 seconds
            self.undo.push()
            self.mov.currentFrame.setDelayValue(delayValue)
        else:
            self.notify("Delay must be between 0-120 seconds.")   

    def deleteCurrentFramePrompt(self):
        self.clearStatusLine()
        self.promptPrint("Are you sure you want to delete the current frame? (Y/N) ")
        prompting = True
        while prompting:
            time.sleep(0.01)
            c = self.stdscr.getch()
            if c == 121:  # 'y'
                prompting = False
                self.undo.push()
                self.mov.deleteCurrentFrame()
                self.clearStatusLine()
                return True
            elif c == 110:    # 'n'
                prompting = False
                self.clearStatusLine()
                return False
            time.sleep(0.01)

    def safeQuit(self):
        self.stdscr.nodelay(0) # wait for input when calling getch
        self.clearStatusLine()
        if self.appState.modified:
            self.promptPrint("Changes have not been saved! Are you sure you want to Quit? (Y/N) " )
        else:
            self.promptPrint("Are you sure you want to Quit? (Y/N) " )
        prompting = True
        while prompting:
            time.sleep(0.01)
            c = self.stdscr.getch()
            if c == 121:   # 121 = y
                exiting = True
                prompting = False
            elif c == 110: # 110 = n
                exiting = False
                prompting = False
            time.sleep(0.01)
        self.clearStatusLine()
        if exiting:
            self.verySafeQuit()

    def verySafeQuit(self): # non-interactive part.. close out curses screen and exit.
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.echo()
        curses.endwin()
        exit(0)

    def promptPrint(self, promptText):
        """ Prints prompting text in a consistent manner """
        self.addstr(self.statusBarLineNum, 0, promptText, curses.color_pair(self.appState.theme['promptColor']))

    def openMenu(self, current_menu: str):
        menu_open = True
        response = "Right"
        menus = ["File", "Mouse Tools"]
        #fail_count = 0  # debug
        while menu_open:
            if current_menu == "File":
                response = self.statusBar.menuButton.on_click()
                self.statusBar.menuButton.draw()    # redraw as unselected/not-inverse
            elif current_menu == "Mouse Tools":
                response = self.statusBar.toolButton.on_click()
                self.statusBar.toolButton.draw()    # redraw as unselected/not-inverse
            if response == "Close":
                menu_open = False
            elif response == "Right":
                # if we're at the rightmost menu
                if menus.index(current_menu) == len(menus) - 1:
                    current_menu = menus[0] # circle back around
                else:
                    next_menu_index = menus.index(current_menu) + 1
                    current_menu = menus[next_menu_index]
            elif response == "Left":
                # If we're at the leftmose menu
                if menus.index(current_menu) == 0:
                    next_menu_index = len(menus) - 1
                    current_menu = menus[next_menu_index]
                else:
                    next_menu_index = menus.index(current_menu) - 1
                    current_menu = menus[next_menu_index]
            #fail_count += 1 # debug
            #if fail_count > 3:
            #    pdb.set_trace()

    def openFromMenu(self):
        load_filename = self.openFilePicker()
        if load_filename:   # if not False
            self.clearCanvas(prompting=False)
            self.loadFromFile(load_filename, 'dur')
            self.move_cursor_topleft()

    def showCharSetPicker(self):
        set_list = ["Durdraw Default"]
        block_list = self.appState.unicodeBlockList.copy()

        for set_name in set_list:
            block_list.insert(0, set_name)
        
        # draw ui
        selected_item_number = 0
        current_line_number = 0
        search_string = ""
        mask_all = False
        top_line = 0    # topmost viewable line, for scrolling
        prompting = True
        # Turn on keyboard buffer waiting here, if necessary..
        self.stdscr.nodelay(0)
        self.stdscr.clear()
        while prompting:
            # draw list of files from top of the window to bottomk
            realmaxY,realmaxX = self.realstdscr.getmaxyx()
            page_size = realmaxY - 4
            current_line_number = 0
            if selected_item_number > top_line + page_size-1 or selected_item_number < top_line: # item is off the screen
                top_line = selected_item_number - int(page_size-3) # scroll so it's at the bottom
            for blockname in block_list:
                if current_line_number >= top_line and current_line_number - top_line < page_size:  # If we're within screen size
                    currentActiveSet = False
                    if blockname == self.appState.characterSet:     # currently used character set
                        currentActiveSet = True
                        block_label = f"{block_list[current_line_number]} *"
                    elif self.appState.characterSet == "Unicode Block" and blockname == self.appState.unicodeBlock:
                        currentActiveSet = True
                        block_label = f"{block_list[current_line_number]} *"
                    else:
                        block_label = block_list[current_line_number]
                    if  selected_item_number == current_line_number:    # if block is selected
                        self.addstr(current_line_number - top_line, 0, block_label, curses.A_REVERSE)
                    else:
                        if block_list[current_line_number] in set_list:
                            if currentActiveSet:     # currently used character set
                                self.addstr(current_line_number - top_line, 0, block_label, curses.color_pair(self.appState.theme['menuTitleColor']) | curses.A_BOLD)
                            else:
                                self.addstr(current_line_number - top_line, 0, block_label, curses.color_pair(self.appState.theme['menuTitleColor']))
                        else:
                            if currentActiveSet:
                                self.addstr(current_line_number - top_line, 0, block_label, curses.color_pair(self.appState.theme['promptColor']) | curses.A_BOLD)
                            else:
                                self.addstr(current_line_number - top_line, 0, block_label, curses.color_pair(self.appState.theme['promptColor']))
                current_line_number += 1

            #if mask_all:
            #    self.addstr(realmaxY - 4, 0, f"[X]", curses.color_pair(self.appState.theme['clickColor']))
            #else:
            #    self.addstr(realmaxY - 4, 0, f"[ ]", curses.color_pair(self.appState.theme['clickColor']))
            #self.addstr(realmaxY - 4, 4, f"Show All Files", curses.color_pair(self.appState.theme['menuItemColor']))
            #self.addstr(realmaxY - 4, 20, f"[PGUP]", curses.color_pair(self.appState.theme['clickColor']))
            #self.addstr(realmaxY - 4, 27, f"[PGDOWN]", curses.color_pair(self.appState.theme['clickColor']))
            #self.addstr(realmaxY - 4, 36, f"[OK]", curses.color_pair(self.appState.theme['clickColor']))
            #self.addstr(realmaxY - 4, 41, f"[CANCEL]", curses.color_pair(self.appState.theme['clickColor']))
            #self.addstr(realmaxY - 3, 0, f"Folder: {current_directory}", curses.color_pair(self.appState.theme['menuTitleColor']))
            if search_string != "":
                self.addstr(realmaxY - 2, 0, f"search: ")
                self.addstr(realmaxY - 2, 8, f"{search_string}", curses.color_pair(self.appState.theme['menuItemColor']))
            # print preview characters
            errorLoadingBlock = False
            if block_list[selected_item_number] in set_list:    # not a unicode block
                errorLoadingBlock = False
                self.addstr(realmaxY - 1, 0, f"Character set: {block_list[selected_item_number]}")
            else:
                previewCharMap = durchar.load_unicode_block(block_list[selected_item_number])
                self.addstr(realmaxY - 1, 0, f"Unicode block: {block_list[selected_item_number]}")
                previewChars = "Preview: "
                maxChars = 100
                totalChars = 0
                for miniMap in previewCharMap:  # for all characters in this block...
                    for key in miniMap:
                        if totalChars <= maxChars:  # If we're within range,
                            previewChars += chr(miniMap[key])   # add to the preview string
                        totalChars += 1 
                try:
                    self.addstr(realmaxY - 4, 0, previewChars)
                    errorLoadingBlock = False
                except Exception as E:
                    errorLoadingBlock = True
                    self.addstr(realmaxY - 4, 0, "Cannot load this block")

            self.stdscr.refresh()
            c = self.stdscr.getch()
            self.stdscr.clear()
            if c == curses.KEY_LEFT:
                pass
            elif c == curses.KEY_RIGHT:
                pass
            elif c == curses.KEY_UP:
                # move cursor up
                if selected_item_number > 0:
                    if selected_item_number == top_line and top_line != 0:
                        top_line -= 1
                    selected_item_number -= 1
                pass
            elif c == curses.KEY_DOWN:
                if selected_item_number < len(block_list) - 1:
                    # move cursor down
                    selected_item_number += 1
                    # if we're at the bottom of the screen...
                    if selected_item_number - top_line == page_size and top_line < len(block_list) - page_size:
                        top_line += 1
            elif c in [339, curses.KEY_PPAGE]:  # page up
                if selected_item_number - top_line > 0:  # first go to the top of the page
                    selected_item_number = top_line
                else:   # if already there, go up a full page
                    selected_item_number -= page_size
                    top_line -= page_size 
                # correct any overflow
                if selected_item_number < 0:
                    selected_item_number = 0
                if top_line < 0:
                    top_line = 0
            elif c in [338, curses.KEY_NPAGE]:  # page down
                if selected_item_number - top_line < page_size - 1: # first go to bottom of the page
                    selected_item_number = page_size + top_line - 1
                else:   # if already there, go down afull page
                    selected_item_number += page_size
                    top_line += page_size
                # correct any overflow
                if selected_item_number >= len(block_list):
                    selected_item_number = len(block_list) - 1
                if top_line >= len(block_list):
                    top_line = len(block_list) - page_size
            elif c in [339, curses.KEY_HOME]:  # 339 = home
                selected_item_number = 0
                top_line = 0
            elif c in [338, curses.KEY_END]:   # 338 = end
                selected_item_number = len(block_list) - 1
                top_line = selected_item_number - page_size + 1
                if top_line < 0:    # for small file lists
                    top_line = 0
            elif c in [13, curses.KEY_ENTER]:
                if errorLoadingBlock:
                    pass
                elif block_list[selected_item_number] in set_list:
                    # Durdraw character set selected. Set it
                    self.setCharacterSet(block_list[selected_item_number])
                    #self.appState.characterSet = block_list[selected_item_number]
                    self.charMapNumber = 0
                    self.initCharSet()
                    self.stdscr.clear()
                    prompting = False
                else:
                    # Unicode block selected.
                    self.appState.characterSet = "Unicode Block"
                    self.charMapNumber = 0
                    self.appState.unicodeBlock = block_list[selected_item_number]
                    self.setUnicodeBlock(block=self.appState.unicodeBlock)
                    self.stdscr.clear()
                    prompting = False
                    #pdb.set_trace()
                    #full_path = f"{current_directory}/{block_list[selected_item_number]}"
                    #return full_path
            elif c == 27:   # esc key
                if search_string != "":
                    search_string = ""
                else:
                    self.stdscr.clear()
                    prompting = False
                    if self.playing:
                        elf.stdscr.nodelay(1)
                    return False
            elif c in [' curses.KEY_BACKSPACE', 263, 127]: # backspace
                if search_string != "":
                    # if string is not empty, remove last character
                    search_string = search_string[:len(search_string)-1]
            elif c == curses.KEY_MOUSE:
                try:
                    _, mouseCol, mouseLine, _, mouseState = curses.getmouse()
                except:
                    pass
                if mouseState == curses.BUTTON1_CLICKED or mouseState == curses.BUTTON1_DOUBLE_CLICKED:
                    if mouseLine < realmaxY - 4:     # above the 'status bar,' in the file list
                        if mouseLine < len(block_list) - top_line:   # clicked item line
                            if mouseCol < len(block_list[top_line+mouseLine]): # clicked within item width
                                selected_item_number = top_line+mouseLine
                                if mouseState == curses.BUTTON1_DOUBLE_CLICKED:
                                    if block_list[selected_item_number] in set_list:    # clicked set, not block
                                        # holy fuck this is deep
                                        self.appState.characterSet = block_list[selected_item_number]
                                        self.charMapNumber = 0
                                        self.initCharSet()
                                        self.stdscr.clear()
                                        prompting = False
                                    else:   # clicked a unicode block
                                        self.appState.characterSet = "Unicode Block"
                                        self.charMapNumber = 0
                                        self.setUnicodeBlock(block=block_list[selected_item_number])
                                        self.stdscr.clear()
                                        prompting = False
                    #if mouseLine == realmaxY - 4:    # on the button bar
                    #    if mouseCol in range(0,3):  # clicked [X] All
                    #        if mask_all:
                    #            mask_all = False
                    #            masks = default_masks
                    #        else:
                    #            mask_all = True
                    #            masks = ['*.*']
                        # update file list
                elif mouseState & curses.BUTTON4_PRESSED:   # wheel up
                    # scroll up
                    # if the item isn't at the top of teh screen, move it up
                    if selected_item_number > top_line:
                        selected_item_number -= 1
                    elif top_line > 0:
                        top_line -= 1
                elif mouseState & curses.BUTTON5_PRESSED:   # wheel down
                    # scroll down 
                    if selected_item_number < len(block_list) - 1:
                        selected_item_number += 1
                        if selected_item_number == len(block_list) - top_line:
                            top_line += 1
            else: # add to search string
                search_string += chr(c)
                search_string = search_string.lower()   # case insensitive search
                for blockname in block_list:  # search list for search_string
                    # prioritize unicode block names for some reason
                    if blockname not in set_list and blockname.lower().startswith(search_string):
                        selected_item_number = block_list.index(blockname)
                        break   # stop at the first match
                    # then search character sets
                    elif blockname in set_list and blockname.lower().startswith(search_string):
                        selected_item_number = block_list.index(blockname)
                        break   # stop at the first match
                    # Finally if nothing begins with the search string, see if
                    # any items contain the search string
                    elif search_string in blockname.lower():
                        selected_item_number = block_list.index(blockname)
                        break   # stop at the first match

    def openFilePicker(self):
        """ Draw UI for selecting a file to load, return the filename """
        # get file list
        folders =  ["../"]
        folders += glob.glob("*/")
        default_masks = ['*.dur', '*.asc', '*.ans', '*.txt', '*.diz']
        masks = default_masks
        current_directory = os.getcwd()
        matched_files = []
        file_list = []
        for file in os.listdir(current_directory):
            for mask in masks:
                if fnmatch.fnmatch(file.lower(), mask.lower()):
                    matched_files.append(file)
                    break
        for dirname in folders:
            file_list.append(dirname)
        file_list += sorted(matched_files)

        # draw ui
        selected_item_number = 0
        current_line_number = 0
        search_string = ""
        mask_all = False
        top_line = 0    # topmost viewable line, for scrolling
        prompting = True
        # Turn on keyboard buffer waiting here, if necessary..
        self.stdscr.nodelay(0)
        self.stdscr.clear()
        while prompting:
            # draw list of files from top of the window to bottomk
            realmaxY,realmaxX = self.realstdscr.getmaxyx()
            page_size = realmaxY - 4
            current_line_number = 0
            if selected_item_number > top_line + page_size-1 or selected_item_number < top_line: # item is off the screen
                top_line = selected_item_number - int(page_size-3) # scroll so it's at the bottom
            for filename in file_list:
                if current_line_number >= top_line and current_line_number - top_line < page_size:  # If we're within screen size
                    if  selected_item_number == current_line_number:    # if file is selected
                        self.addstr(current_line_number - top_line, 0, file_list[current_line_number], curses.A_REVERSE)
                    else:
                        if file_list[current_line_number] in folders:
                            self.addstr(current_line_number - top_line, 0, file_list[current_line_number], curses.color_pair(self.appState.theme['menuTitleColor']))
                        else:
                            self.addstr(current_line_number - top_line, 0, file_list[current_line_number], curses.color_pair(self.appState.theme['promptColor']))
                current_line_number += 1

            if mask_all:
                self.addstr(realmaxY - 4, 0, f"[X]", curses.color_pair(self.appState.theme['clickColor']))
            else:
                self.addstr(realmaxY - 4, 0, f"[ ]", curses.color_pair(self.appState.theme['clickColor']))
            self.addstr(realmaxY - 4, 4, f"Show All Files", curses.color_pair(self.appState.theme['menuItemColor']))
            #self.addstr(realmaxY - 4, 20, f"[PGUP]", curses.color_pair(self.appState.theme['clickColor']))
            #self.addstr(realmaxY - 4, 27, f"[PGDOWN]", curses.color_pair(self.appState.theme['clickColor']))
            #self.addstr(realmaxY - 4, 36, f"[OK]", curses.color_pair(self.appState.theme['clickColor']))
            #self.addstr(realmaxY - 4, 41, f"[CANCEL]", curses.color_pair(self.appState.theme['clickColor']))
            self.addstr(realmaxY - 3, 0, f"Folder: {current_directory}", curses.color_pair(self.appState.theme['menuTitleColor']))
            if search_string != "":
                self.addstr(realmaxY - 2, 0, f"search: ")
                self.addstr(realmaxY - 2, 8, f"{search_string}", curses.color_pair(self.appState.theme['menuItemColor']))
            # debug
            self.addstr(realmaxY - 1, 0, f"filename: {file_list[selected_item_number]}")

            self.stdscr.refresh()
            c = self.stdscr.getch()
            self.stdscr.clear()
            if c == curses.KEY_LEFT:
                pass
            elif c == curses.KEY_RIGHT:
                pass
            elif c == curses.KEY_UP:
                # move cursor up
                if selected_item_number > 0:
                    if selected_item_number == top_line and top_line != 0:
                        top_line -= 1
                    selected_item_number -= 1
                pass
            elif c == curses.KEY_DOWN:
                if selected_item_number < len(file_list) - 1:
                    # move cursor down
                    selected_item_number += 1
                    # if we're at the bottom of the screen...
                    if selected_item_number - top_line == page_size and top_line < len(file_list) - page_size:
                        top_line += 1
            elif c in [339, curses.KEY_PPAGE]:  # page up
                if selected_item_number - top_line > 0:  # first go to the top of the page
                    selected_item_number = top_line
                else:   # if already there, go up a full page
                    selected_item_number -= page_size
                    top_line -= page_size 
                # correct any overflow
                if selected_item_number < 0:
                    selected_item_number = 0
                if top_line < 0:
                    top_line = 0
            elif c in [338, curses.KEY_NPAGE]:  # page down
                if selected_item_number - top_line < page_size - 1: # first go to bottom of the page
                    selected_item_number = page_size + top_line - 1
                else:   # if already there, go down afull page
                    selected_item_number += page_size
                    top_line += page_size
                # correct any overflow
                if selected_item_number >= len(file_list):
                    selected_item_number = len(file_list) - 1
                if top_line >= len(file_list):
                    top_line = len(file_list) - page_size
            elif c in [339, curses.KEY_HOME]:  # 339 = home
                selected_item_number = 0
                top_line = 0
            elif c in [338, curses.KEY_END]:   # 338 = end
                selected_item_number = len(file_list) - 1
                top_line = selected_item_number - page_size + 1
                if top_line < 0:    # for small file lists
                    top_line = 0
            elif c in [13, curses.KEY_ENTER]:
                if file_list[selected_item_number] in folders:
                    # change directories
                    if file_list[selected_item_number] == "../":
                        # "cd .."
                        current_directory = os.path.split(current_directory)[0]
                    else:
                        current_directory = f"{current_directory}/{file_list[selected_item_number]}"
                        if current_directory[-1] == "/":
                            current_directory = current_directory[:-1]
                    # get file list
                    folders =  ["../"]
                    folders += glob.glob("*/", root_dir=current_directory)
                    if mask_all:
                        masks = ['*.*']
                    else:
                        masks = default_masks
                    matched_files = []
                    file_list = []
                    for file in os.listdir(current_directory):
                        for mask in masks:
                            if fnmatch.fnmatch(file.lower(), mask.lower()):
                                matched_files.append(file)
                                break
                    for dirname in folders:
                        file_list.append(dirname)
                    file_list += sorted(matched_files)
                    # reset ui
                    selected_item_number = 0
                    search_string = ""
                else:
                    # return the selected file
                    self.stdscr.clear()
                    prompting = False
                    full_path = f"{current_directory}/{file_list[selected_item_number]}"
                    return full_path
            elif c == 27:   # esc key
                if search_string != "":
                    search_string = ""
                else:
                    self.stdscr.clear()
                    prompting = False
                    if self.playing:
                        elf.stdscr.nodelay(1)
                    return False
            elif c in [' curses.KEY_BACKSPACE', 263, 127]: # backspace
                if search_string != "":
                    # if string is not empty, remove last character
                    search_string = search_string[:len(search_string)-1]
            elif c == curses.KEY_MOUSE:
                try:
                    _, mouseCol, mouseLine, _, mouseState = curses.getmouse()
                except:
                    pass
                if mouseState == curses.BUTTON1_CLICKED or mouseState == curses.BUTTON1_DOUBLE_CLICKED:
                    if mouseLine < realmaxY - 4:     # above the 'status bar,' in the file list
                        if mouseLine < len(file_list) - top_line:   # clicked item line
                            if mouseCol < len(file_list[top_line+mouseLine]): # clicked within item width
                                selected_item_number = top_line+mouseLine
                                if mouseState == curses.BUTTON1_DOUBLE_CLICKED:
                                    if file_list[selected_item_number] in folders:  # clicked directory
                                        # change directories. holy fuck this is deep
                                        if file_list[selected_item_number] == "../":
                                            # "cd .."
                                            current_directory = os.path.split(current_directory)[0]
                                        else:
                                            current_directory = f"{current_directory}/{file_list[selected_item_number]}"
                                            if current_directory[-1] == "/":
                                                current_directory = current_directory[:-1]
                                        # get file list
                                        folders =  ["../"]
                                        folders += glob.glob("*/", root_dir=current_directory)
                                        if mask_all:
                                            masks = ['*.*']
                                        else:
                                            masks = default_masks
                                        matched_files = []
                                        file_list = []
                                        for file in os.listdir(current_directory):
                                            for mask in masks:
                                                if fnmatch.fnmatch(file.lower(), mask.lower()):
                                                    matched_files.append(file)
                                                    break
                                        for dirname in folders:
                                            file_list.append(dirname)
                                        file_list += sorted(matched_files)
                                        # reset ui
                                        selected_item_number = 0
                                        search_string = ""
                                    else:   # clicked a file, try to load it
                                        full_path = f"{current_directory}/{file_list[selected_item_number]}"
                                        return full_path
                    if mouseLine == realmaxY - 4:    # on the button bar
                        if mouseCol in range(0,3):  # clicked [X] All
                            if mask_all:
                                mask_all = False
                                masks = default_masks
                            else:
                                mask_all = True
                                masks = ['*.*']
                        # update file list
                        matched_files = []
                        file_list = []
                        for file in os.listdir(current_directory):
                            for mask in masks:
                                if fnmatch.fnmatch(file.lower(), mask.lower()):
                                    matched_files.append(file)
                                    break
                        for dirname in folders:
                            file_list.append(dirname)
                        file_list += sorted(matched_files)
                        # reset ui
                        selected_item_number = 0
                        search_string = ""
                elif mouseState & curses.BUTTON4_PRESSED:   # wheel up
                    # scroll up
                    # if the item isn't at the top of teh screen, move it up
                    if selected_item_number > top_line:
                        selected_item_number -= 1
                    elif top_line > 0:
                        top_line -= 1
                elif mouseState & curses.BUTTON5_PRESSED:   # wheel down
                    # scroll down 
                    if selected_item_number < len(file_list) - 1:
                        selected_item_number += 1
                        if selected_item_number == len(file_list) - top_line:
                            top_line += 1
            else: # add to search string
                search_string += chr(c)
                for filename in file_list:  # search list for search_string
                    if filename not in folders and filename.startswith(search_string):
                        selected_item_number = file_list.index(filename)
                        break   # stop at the first match

    def open(self):
        self.clearStatusLine()
        if self.appState.modified:
            self.promptPrint("Changes have not been saved! Are you sure you want to load another file? (Y/N) ")
            prompting = True
            while prompting:
                time.sleep(0.01)
                c = self.stdscr.getch()
                if c == 121:   # 121 = y
                    prompting = False
                elif c == 110 or c == 27: # 110 == n, 27 == esc
                    prompting = False
                    return None
                time.sleep(0.01)
            self.clearStatusLine()

        self.move(self.mov.sizeY, 0)
        self.stdscr.nodelay(0) # wait for input when calling getch
        self.promptPrint("File format? [I] ASCII, [D] DUR (or JSON), [ESC] Cancel: ")
        prompting = True
        while prompting:
            c = self.stdscr.getch()
            time.sleep(0.01)
            if c == 105:   # 105 i = ascii
                loadFormat = 'ascii'
                prompting = False
            elif c == 100: # 100 = d = dur
                loadFormat = 'dur'
                prompting = False
            elif c == 27: # 27 = esc = cancel
                self.clearStatusLine()
                prompting = False
                return None
        self.clearStatusLine()
        self.promptPrint("Enter file name to open: ")
        curses.echo()
        shortfile = self.stdscr.getstr().decode('utf-8')
        curses.noecho()
        if shortfile.replace(' ', '') == '':
            self.notify("File name cannot be empty.")
            return False
        self.clearStatusLine()
        if not self.loadFromFile(shortfile, loadFormat):
            return False
        self.undo = UndoManager(self, appState = self.appState) # reset undo system
        self.stdscr.redrawwin()
        self.stdscr.clear()
        self.refresh()      # so we can see the new ascii in memory.

    def convertToCurrentFormat(self, fileColorMode = None):   # should this and loadFromFile be in a
        # separate class for file operations? or into Movie() or Options() ?
        # then loadFromFile could return a movie object instead.
        """ If we load old .dur files, convert to the latest format """
        # aka "fill in the blanks"
        if self.appState.debug: self.notify(f"Converting to new format. Current format: {self.opts.saveFileFormat}")
        if self.opts.saveFileFormat < 3:  # version 4 should rename saveFileFormat
            if self.appState.debug: self.notify(f"Upgrading to format 3. Making old color map.")
            # to saveFormatVersion
            # initialize color map for all frames:
            for frame in self.mov.frames:  
                frame.initColorMap()    
                self.opts.saveFileFormat = 3
        if self.opts.saveFileFormat < 4:
            if self.appState.debug: self.notify(f"Upgrading to format 4. Adding delays.")
            # old file, needs delay times populated.
            for frame in self.mov.frames:
                frame.setDelayValue(0)
                self.opts.saveFileFormat = 4
        if self.opts.saveFileFormat < 5:
            if self.appState.debug: self.notify(f"Upgrading to format 5. Making new color map.")
            for frame in self.mov.frames:
                frame.newColorMap = durmovie.convert_dict_colorMap(frame.colorMap, frame.sizeX, frame.sizeY)
            self.opts.saveFileFormat = 5
        if self.opts.saveFileFormat < 6:
            if self.appState.debug: self.notify(f"Upgrading to format 6. Making new color map.")
            for frame in self.mov.frames:
                try:
                    frame.height    # for really old pickle files
                except:
                    frame.height = frame.sizeY
                    frame.width = frame.sizeY
                for line in range(0, frame.height):
                    for col in range(0, frame.width):
                        oldPair = frame.newColorMap[line][col]
                        oldMode = self.appState.colorMode
            self.opts.saveFileFormat = 6
        convertedColorMap = False
        if self.opts.saveFileFormat < 7:
            if self.appState.debug: self.notify(f"Upgrading to format 7. Converting color map.")
            if self.mov.contains_high_colors():
                if self.appState.debug: self.notify(f"Old file format was 256 color.")
                self.ansi.convert_colormap(self.mov, dur_ansilib.legacy_256_to_256)
            else:
                if self.appState.colorMode == '16':
                    if self.appState.debug: self.notify(f"Old file format was 16 color. Converting to new 16.")
                    self.ansi.convert_colormap(self.mov, dur_ansilib.legacy_16_to_16)
                    convertedColorMap = True
                else:
                    if self.appState.debug: self.notify(f"Old file format was 16 color. Converting to new 256.")
                    self.ansi.convert_colormap(self.mov, dur_ansilib.legacy_16_to_256)
                    convertedColorMap = True
            self.opts.saveFileFormat = 7
        if fileColorMode == "16" and self.appState.colorMode == "256" and convertedColorMap == False:
            for frame in self.mov.frames:   # conert from 16 to 256 pallette
                for line in range(0, frame.height):
                    for col in range(0, frame.width):
                        if frame.newColorMap[line][col][0] == 1:   # convert black color
                            frame.newColorMap[line][col][0] = 16
                        frame.newColorMap[line][col][0] = frame.newColorMap[line][col][0] - 1   # convert rest of colors
                        if frame.newColorMap[line][col][1] == 1:   # convert black color
                            frame.newColorMap[line][col][1] = 16
                        frame.newColorMap[line][col][1] = frame.newColorMap[line][col][1] - 1   # convert rest of colors


        
        self.opts.saveFileFormat = self.appState.durFileVer

    def loadFromFile(self, shortfile, loadFormat):  # shortfile = non full path filename
        filename = os.path.expanduser(shortfile)
        if loadFormat == 'ascii': # or ANSI...
            try:
                if self.appState.debug: self.notify("Trying to open() file as ascii.")
                f = open(filename, 'r')
                self.appState.curOpenFileName = os.path.basename(filename)
            except Exception as e:
                #if self.appState.debug: self.notify(f"self.opts = pickle.load(f)")
                self.notify(f"Could not open file for reading: {e}")
                return None
            # here we add the stuff to load the file into self.mov.currentFrame.content[][]
            self.undo.push()
            if self.appState.colorMode == '256':
                fg, bg = 7, 0
            elif self.appState.colorMode == '16':
                fg, bg = 8, 0
            lineNum = 0
            colNum = 0
            i = 0
            try:
                raw_text = f.read() 
            except UnicodeDecodeError:
                f.close()
                if self.appState.charEncoding == 'utf-8':
                    self.notify("This appears to be a CP437 ANSI/ASCII - Converting to Unicode.")
                f = open(filename, 'r', encoding='cp437')
                raw_text = f.read()
            # Load file into a new frame, make a new movie,
            newFrame = dur_ansiparse.parse_ansi_escape_codes(raw_text, appState=self.appState, caller=self, debug=self.appState.debug)
            self.appState.topLine = 0
            newMovieOpts = Options(width=newFrame.width, height=newFrame.height)
            newMovie = Movie(newMovieOpts)
            # add the frame with the loaded ANSI file to the movie
            newMovie.addFrame(newFrame)
            newMovie.deleteCurrentFrame()   # remove the blank first frame

            self.mov = newMovie

            f.close()
            #self.notify(f"From color map at 1, 1: {self.mov.currentFrame.newColorMap[1][1]}")
            #for x in range(lineNum, self.mov.sizeY):   # clear out rest of contents.
            #    self.mov.currentFrame.content[x] = list(" " * self.mov.sizeX)
        elif loadFormat == 'dur':
            try:
                f = open(filename, 'rb')
            except Exception as e:
                self.notify(f"Could not open file for reading: {type(e)}: {e}")
                return None
            # check for gzipped file
            f.seek(0)
            fileHeader = f.read(2)
            if self.appState.debug: self.notify(f"File header: {fileHeader.hex()}")
            if self.appState.debug: self.notify(f"Checking for gzip file...")
            if fileHeader == b'\x1f\x8b': # gzip magic numbers
                if self.appState.debug: self.notify(f"gzip found")
                # file == gzip compressed
                f.close()
                try:
                    f = gzip.open(filename, 'rb')
                    f.seek(0)
                    if self.appState.debug: self.notify(f"Un-gzipped successfully")
                except Exception as e:
                    self.notify(f"Could not open file for reading as gzip: {type(e)}: {e}", pause=True)
            else:
                if self.appState.debug: self.notify(f"gzip NOT found")
                #f.seek(0)
            # check for JSON Durdraw file
            #if (f.read(16) == b'\x7b\x0a\x20\x20\x22\x44\x75\x72\x64\x72\x61\x77\x20\x4d\x6f\x76'): # {.  "Durdraw Mov
            if self.appState.debug: self.notify(f"Checking for JSON file.")
            f.seek(0)
            if f.read(12) == b'\x7b\x0a\x20\x20\x22\x44\x75\x72\x4d\x6f\x76\x69': # {.  "DurMov
                if self.appState.debug: self.notify(f"JSON found. Loading JSON dur file.")
                f.seek(0)
                fileColorMode, fileCharEncoding = durfile.get_dur_file_colorMode_and_charMode(f)

                if fileColorMode == "256" and fileColorMode != self.appState.colorMode:
                    self.notify(f"Warning: Loading a 256 color file in 16 color mode. Some colors may not be displayed.")

                if fileCharEncoding != self.appState.charEncoding:
                    self.notify(f"Warning: File uses {fileCharEncoding} character encoding, but Durdraw is in {self.appState.charEncoding} mode.")
                newMovie =  durfile.open_json_dur_file(f, self.appState)
                self.opts = newMovie['opts']
                self.mov = newMovie['mov']
                self.setPlaybackRange(1, self.mov.frameCount)
                if self.appState.debug: self.notify(f"{self.opts}")
                if self.appState.debug: self.notify(f"Finished loading JSON dur file")
                self.appState.curOpenFileName = os.path.basename(filename)
                self.appState.modified = False
                self.setWindowTitle(shortfile)
                self.convertToCurrentFormat(fileColorMode = fileColorMode)

                # Convert palettes as necessary
                if fileColorMode == "xterm-256" and fileColorMode != self.appState.colorMode:
                    # Old file format, does not specify whether it's 16 or 256 colors.
                    fileColorMode = "256"
                    pass
                if fileColorMode == "16" and fileColorMode != self.appState.colorMode:
                    self.notify(f"Warning: Loading 16 color ANSI in {self.appState.colorMode} color mode will lose background colors.", pause=True)
                return True

            try:    # Maybe it's a really old Pickle file...
                if self.appState.debug: self.notify(f"Unpickling..")
                pickle_fail = False
                f.seek(0)
                unpickler = durfile.DurUnpickler(f)
                if self.appState.debug: self.notify(f"self.opts = unpickler.load()")
                self.opts = unpickler.load()
                if self.appState.debug: self.notify(f"self.mov = unpickler.load()")
                self.mov = unpickler.load()
                if self.appState.debug: self.notify(f"self.appState.curOpenFileName = os.path.basename(filename)")
                self.appState.curOpenFileName = os.path.basename(filename)
                if self.appState.debug: self.notify(f"self.appState.playbackRange = (1,self.mov.frameCount)")
                self.appState.playbackRange = (1,self.mov.frameCount)
            except Exception as e:
                pickle_fail = True
                if self.appState.debug:
                    self.notify(f"Exception in unpickling: {type(e)}: {e}", pause=True)
            # If the first unpickling fails, try looking for another pickle format
            if pickle_fail:
                try:
                    f.seek(0)
                    if self.appState.debug: self.notify(f"self.opts = pickle.load(f ")
                    self.opts = pickle.load(f)
                    if self.appState.debug: self.notify(f"self.mov = pickle.load(f ")
                    self.mov = pickle.load(f)
                    self.appState.playbackRange = (1,self.mov.frameCount)
                    pickle_fail = False
                except Exception as e:
                    if self.appState.debug:
                        self.notify(f"Exception in unpickling other format: {type(e)}: {e}", pause=True)
                    pickle_fail = True

            if pickle_fail: # pickle is still failing
                loadFormat = 'ascii'    # loading .dur format failed, so assume it's ascii instead.
                # change this to ANSI once ANSI file loading works, stripping out ^M in newlines
                # change this whole method to call loadDurFile(), loadAnsiFile(),
                # etc, checking for faiulre.
            self.convertToCurrentFormat()
            f.close()
            if loadFormat == 'ascii':  # loading as dur failed, so load as ascii instead.
                self.loadFromFile(shortfile, loadFormat)
            self.appState.modified = False
        self.setWindowTitle(shortfile)
        self.mov.gotoFrame(1)


    
    def save(self):
        self.clearStatusLine()
        self.move(self.mov.sizeY, 0)
        self.promptPrint("File format? [D]UR, [A]NSI, ASCI[I], [M]IRC, [J]SON, [H]TML, [P]NG, [G]IF: ")
        self.stdscr.nodelay(0) # do not wait for input when calling getch
        prompting = True
        saved = False
        while prompting:
            c = self.stdscr.getch()
            time.sleep(0.01)
            if c in [105, 73]:   # 105 i = ascii
                saveFormat = 'ascii'
                prompting = False
            elif c in [100, 68]: # 100 = d = dur, 68 = D
                saveFormat = 'dur'
                prompting = False
            elif c in [106, 74]:  # 106 = j, 74 = J
                saveFormat = 'json'
                prompting = False
            elif c in [104, 63]:  # 106 = h, 74 = H
                saveFormat = 'html'
                prompting = False
            elif c in [97, 65]: # a = ansi
                saveFormat = 'ansi'
                prompting = False
            elif c in [109]: # m = mIRC
                prompting = False
                if self.mov.contains_high_colors():
                    self.notify("Sorry, mIRC export only works for 16 colors, but this art contains extended colors.", pause=True)
                    return None
                else:
                    saveFormat = 'irc'
            elif c in [112, 80]: # p = png
                saveFormat = 'png'
                prompting = False
            elif c in [103, 71]: # g = gif
                saveFormat = 'gif'
                prompting = False
            elif c == 27: # 27 = esc = cancel
                self.clearStatusLine()
                prompting = False
                return None
        self.clearStatusLine()
        if saveFormat in ['png', 'gif']:
            self.promptPrint("Which font? IBM PC [A]NSI, AM[I]GA: ")
            prompting = True
            while prompting:
                time.sleep(0.01)
                c = self.stdscr.getch()
                time.sleep(0.01)
                if c in [97, 65]: # a/A = ansi
                    saveFont = 'ansi'
                    prompting = False
                elif c in [105, 68]:   # 105 i/I = amiga
                    saveFont = 'amiga'
                    prompting = False
                elif c == 27: # 27 = esc = cancel
                    self.clearStatusLine()
                    prompting = False
                    return None
            if saveFont == 'amiga':
                self.clearStatusLine()
                self.promptPrint("Which amiga font? 1=topaz 2=b-strict, 3=microknight, 4=mosoul, 5=pot-noodle: ")
                prompting = True
                while prompting:
                    c = self.stdscr.getch()
                    time.sleep(0.01)
                    if c == 49: # 1 = topaz
                        saveFont = 'topaz'
                        prompting = False
                    if c == 50: # 2 = b-strict
                        saveFont = 'b-strict'
                        prompting = False
                    if c == 51: # 3 = microknight
                        saveFont = 'microknight'
                        prompting = False
                    if c == 52: # 4 = mosoul
                        saveFont = 'mosoul'
                        prompting = False
                    if c == 53: # 5 = pot-noodle
                        saveFont = 'pot-noodle'
                        prompting = False
                    elif c == 27: # 27 = esc = cancel
                        self.clearStatusLine()
                        prompting = False
                        return None
        self.clearStatusLine()
        self.promptPrint(f"Enter file name to save as ({saveFormat}) [{self.appState.curOpenFileName}]: ")
        curses.echo()
        filename = str(self.stdscr.getstr().decode('utf-8'))
        curses.noecho()
        if filename.replace(' ', '') == '':
            if saveFormat == "dur":
                filename = self.appState.curOpenFileName
            else:
                self.notify("File name cannot be empty.")
                return False
        filename = os.path.expanduser(filename)
        # If file exists.. ask if it should overwrite.
        if os.path.exists(filename):
            self.clearStatusLine()
            self.promptPrint(f"This file already exists. Overwrite? ")
            prompting = True
            while prompting:
                c = self.stdscr.getch()
                time.sleep(0.01)
                if c in [121, 89]: # y or Y
                    prompting = False
                if c in [110, 78]: # n or N
                    prompting = False
                    self.notify("Canceled. File not saved.")
                    return False
        if saveFormat == 'ascii':
            saved = self.saveAsciiFile(filename)
        if saveFormat == 'durOld':   # dur Old = pickled python objects (ew)
            saved = self.saveDurFile(filename)
        if saveFormat == 'dur':   # dur2 = serialized json gzipped
            saved = self.saveDur2File(filename)
        if saveFormat == 'json':   # dur2 = serialized json, plaintext
            saved = self.saveDur2File(filename, gzipped=False)
        if saveFormat == 'html':   # dur2 = serialized json, plaintext
            saved = self.saveHtmlFile(filename, gzipped=False)
        if saveFormat == 'ansi':  # ansi = escape codes for colors+ascii
            saved = self.saveAnsiFile(filename)
        if saveFormat == 'irc':  # ansi = escape codes for colors+ascii
            saved = self.saveAnsiFile(filename, ircColors = True)
        if saveFormat == 'png':  # png = requires ansi love
            saved = self.savePngFile(filename, font=saveFont)
        if saveFormat == 'gif':  # gif = requires PIL
            saved = self.saveGifFile(filename, font=saveFont)
        if saved:
            self.notify("*Saved* (Press any key to continue)", pause=True)
            self.appState.curOpenFileName = os.path.basename(filename)
            self.appState.modified = False
            self.undo.modifications = 0
            self.setWindowTitle(self.appState.curOpenFileName)
        elif not saved:
            self.notify("Save failed.")

    def saveDurFile(self, filename):
        # open and write file
        try:
            f = gzip.open(filename, 'wb')
        except:
            self.notify("Could not open file for writing. (Press any key to continue)", pause=True)
            return False
        pickle.dump(self.opts, f)
        pickle.dump(self.mov, f)
        f.close()
        return True

    def saveHtmlFile(self, filename, gzipped=False):
        # open and write file
        try:
            f = gzip.open(filename, 'w')
        except:
            self.notify("Could not open file for writing. (Press any key to continue)", pause=True)
            return False
        f.close()
        durfile.write_frame_to_html_file(self.mov, self.appState, self.mov.currentFrame, filename, gzipped=gzipped)
        return True

    def saveDur2File(self, filename, gzipped=True):
        # open and write file
        try:
            f = gzip.open(filename, 'w')
        except:
            self.notify("Could not open file for writing. (Press any key to continue)", pause=True)
            return False
        f.close()
        if gzipped:
            durfile.serialize_to_json_file(self.opts, self.appState, self.mov, filename)
        else:
            durfile.serialize_to_json_file(self.opts, self.appState, self.mov, filename, gzipped=False)
        return True

    def saveAsciiFile(self, filename):
        """ Saves to ascii file, strips trailing blank lines """
        try:
            f = open(filename, 'w')
        except:
            self.notify("Could not open file for writing. (Press any key to continue)", pause=True)
            return False
        # rewrite this. rstrip(' ') looks cool, though.
        outBuffer = '\n'.join(''.join(line).rstrip(' ') for line in self.mov.currentFrame.content).rstrip('\n')
        f.write(outBuffer + '\n\n')
        f.close()
        return True

    def saveAnsiFile(self, filename, lastLineNum=False, lastColNum=False, firstColNum=False, firstLineNum=None, ircColors=False):
        """ Saves current frame of current movie to ansi file """
        try:
            f = open(filename, 'w')
        except:
            self.notify("Could not open file for writing. (Press any key to continue)", pause=True)
            return False
        string = ''
        if not lastLineNum: # if we weren't told what lastLineNum is...
            # find it (last line we should save)
            lastLineNum = self.findFrameLastLine(self.mov.currentFrame)
        if not lastColNum:
            lastColNum = self.findFrameLastCol(self.mov.currentFrame)
        if not firstColNum:
            firstColNum = 0 # Don't crop leftmost blank columns
        if not firstLineNum:
            firstLineNum = self.findFrameFirstLine(self.mov.currentFrame)
        for lineNum in range(firstLineNum, lastLineNum):  # y == lines
            for colNum in range(firstColNum, lastColNum):
                char = self.mov.currentFrame.content[lineNum][colNum]
                color = self.mov.currentFrame.newColorMap[lineNum][colNum]
                colorFg = color[0]
                colorBg = color[1]
                if self.appState.colorMode == "256":
                    if self.appState.showBgColorPicker == False:
                        colorBg = 0 # black, I hope
                try:
                    if ircColors:
                        colorCode = self.ansi.getColorCodeIrc(colorFg,colorBg)
                    else:
                        if self.appState.colorMode == "256":
                            colorCode = self.ansi.getColorCode256(colorFg,colorBg)
                        else:
                            colorCode = self.ansi.getColorCode(colorFg,colorBg)
                except KeyError:
                    if ircColors:   # problem? set a default color
                        colorCode = self.ansi.getColorCodeIrc(1,0)
                    else:
                        colorCode = self.ansi.getColorCode(1,0)
                # If we don't have extended ncurses 6 color pairs,
                # we don't have background colors.. so write the background as black/0
                string = string + colorCode + char
            if ircColors:
                string = string + '\n'
            else:
                string = string + '\r\n'
        f.write(string)
        if ircColors:
            string2 = string + '\n'
        else:
            f.write('\033[0m') # color attributes off
            string2 = string + '\r\n'   # final CR+LF (DOS style newlines)
        f.close()
        return True

    def findLastMovieLine(self, movie):    
        """ Cycle through the whole movie, figure out the lowest numbered
            line that == blank on all frames, return that #. Used to trim blank
            lines when saving. """
        movieLastLine = 1
        for frame in movie.frames:
            frameLastLine = self.findFrameLastLine(frame)
            if frameLastLine > movieLastLine:
                movieLastLine = frameLastLine
        return movieLastLine

    def findFirstMovieLine(self, movie):    
        """ Cycle through the whole movie, figure out the highest numbered
            line that == blank on all frames, return that #. Used to trim blank
            lines when saving. """
        movieFirstLine = movie.sizeY
        for frame in movie.frames:
            frameFirstLine = self.findFrameFirstLine(frame)
            if frameFirstLine < movieFirstLine:
                movieFirstLine = frameFirstLine
        return movieFirstLine

    def findFirstMovieCol(self, movie):    
        """ Cycle through the whole movie, figure out the leftmost column that
            == blank on all frames, return that #. Used to trim blank lines
            when saving. """
        movieFirstCol = movie.sizeX
        for frame in movie.frames:
            frameFirstCol = self.findFrameFirstCol(frame)
            if frameFirstCol < movieFirstCol:
                movieFirstCol = frameFirstCol
        return movieFirstCol

    def findLastMovieCol(self, movie):    
        """ Cycle through the whole movie, figure out the rightmost column
            that == blank on all frames, return that #. Used to trim blank
            lines when saving. """
        movieLastCol = 1
        for frame in movie.frames:
            frameLastCol = self.findFrameLastCol(frame)
            if frameLastCol > movieLastCol:
                movieLastCol = frameLastCol
        return movieLastCol

    def findFrameFirstLine(self, frame):
        """ For the given frame, figure out the first non-blank line, return
            that # (aka, first used line of the frame) """
        # start at the first line, work up until we find a character.
        for lineNum in range(0, self.mov.sizeY):
            for colNum in range(0, frame.sizeX):
                if not frame.content[lineNum][colNum] in [' ', '']:
                    return lineNum  # we found a non-empty character
        return 1 # blank frame, only save the first line.

    def findFrameLastLine(self, frame):
        """ For the given frame, figure out the last non-blank line, return
            that # + 1 (aka, last used line of the frame) """
        # start at the last line, work up until we find a character.
        for lineNum in reversed(list(range(0, self.mov.sizeY))):
            for colNum in range(0, frame.sizeX):
                if not frame.content[lineNum][colNum] in [' ', '']:
                    return lineNum + 1  # we found a non-empty character
        return 1 # blank frame, only save the first line.

    def findFrameLastCol(self, frame):
        """ For the given frame, figure out the last non-blank column, return
            that # + 1 (aka, last used column of the frame) """
        # start at the last column, work back until we find a character.
        for colNum in reversed(list(range(0, frame.sizeX))):
            for lineNum in reversed(list(range(0, self.mov.sizeY))):
                if not frame.content[lineNum][colNum] in [' ', '']:
                    return colNum + 1  # we found a non-empty character
        return 1 # blank frame, only save the first line.

    def findFrameFirstCol(self, frame):
        """ For the given frame, figure out the first non-blank column, return
            that # (aka, first used column of the frame) """
        # start at the first column, work forward until we find a character.
        for colNum in range(0, frame.sizeX):
            for lineNum in range(0, self.mov.sizeY):
                if not frame.content[lineNum][colNum] in [' ', '']:
                    return colNum  # we found a non-empty character
        return 1 # blank frame, only save the first line.

    def savePngFile(self, filename, lastLineNum=None, firstLineNum=None, firstColNum=None, lastColNum=None, font='ansi'):
        """ Save to ANSI then convert to PNG """
        if not self.appState.isAppAvail("ansilove"):   # ansilove not found
            self.notify("Ansilove not found in path. Please find it at http://ansilove.sourceforge.net/", pause=True)
            return False
        tmpAnsiFileName = filename + '.tmp.ans' # remove this file when done
        tmpPngFileName = filename + '.tmp.ans.png' # remove this file when done
        if not self.saveAnsiFile(tmpAnsiFileName, lastLineNum=lastLineNum, firstLineNum=firstLineNum, firstColNum=firstColNum, lastColNum=lastColNum):
            self.notify("Saving ansi failed, make sure you can write to current directory.")
            return False
        devnull = open('/dev/null', 'w')
        if font == 'ansi':
            ansiLoveReturn = subprocess.call(['ansilove', tmpAnsiFileName, tmpPngFileName], stdout=devnull)
        else:   # amiga font
            ansiLoveReturn = subprocess.call(['ansilove', tmpAnsiFileName, "-f", font], stdout=devnull)
        devnull.close()
        os.remove(tmpAnsiFileName)
        if ansiLoveReturn == 0: # this doesnt seem right either, as ansilove always
            pass                  # returns True. 
        else:
            self.notify("Ansilove didn't return success.")
            return False    # stop trying to save png
        # crop out rightmost blank space
        if not lastColNum:
            lastColNum = self.findFrameLastCol(self.mov.currentFrame)
        if not firstColNum:
            firstColNum = self.findFrameFirstCol(self.mov.currentFrame)
        characterWidth = 8  # 9 pixels wide
        cropImage = Image.open(tmpPngFileName)
        cropWidthPixels = (lastColNum - firstColNum) * characterWidth # right
        w,h = cropImage.size
        cropBox = (0, 0, cropWidthPixels, h)  # should be right
        cropImage = cropImage.crop(cropBox)
        finalImage = open(filename, 'wb')
        try:
            cropImage.save(finalImage, "png")
            #self.notify("Saved successfully!")
            finalImage.close()
        except:
            self.notify("Error: Could not crop png.")
            os.remove(tmpPngFileName)
            return False
        os.remove(tmpPngFileName)
        return True


    def saveGifFile(self, filename, font="ansi"):
        try:    # check for PIL/pillow
            import PIL
        except ImportError:
            self.notify("Error: Please install the PIL python module.")
            return False
        tmpPngNames = []
        # switch to first frame
        self.mov.currentFrameNumber = 1
        self.mov.currentFrame = self.mov.frames[self.mov.currentFrameNumber - 1]
        self.refresh()
        firstMovieLineNum = self.findFirstMovieLine(self.mov) # so we can trim
        lastMovieLineNum = self.findLastMovieLine(self.mov) 
        firstMovieColNum = self.findFirstMovieCol(self.mov)
        lastMovieColNum = self.findLastMovieCol(self.mov) 
        for num in range(1, self.mov.frameCount + 1):   # then for each frame
            # make a temp png filename and add it to the list
            tmpPngName = filename + "." + str(num) + ".png"
            tmpPngNames.append(tmpPngName)
            # save the png
            if not self.savePngFile(tmpPngName, lastLineNum=lastMovieLineNum, firstLineNum=firstMovieLineNum, firstColNum=firstMovieColNum, lastColNum=lastMovieColNum, font=font):
                return False
            # If frame has a delay, copy saved file FPS times and add new
            # file names to tmpPngNames.
            if self.mov.currentFrame.delay > 0:
                numOfDelayFramesToAdd = int(self.mov.currentFrame.delay) * int(self.opts.framerate)
                for delayFrameNum in range(1,int(self.mov.currentFrame.delay) * \
                        int(self.opts.framerate)):
                    # eg: 2 second delay, 8fps, means add 16 frames.
                    delayFramePngName = tmpPngName + str(delayFrameNum) + ".png"
                    shutil.copy(tmpPngName, delayFramePngName)
                    tmpPngNames.append(delayFramePngName)
            # go to next frame
            self.mov.nextFrame()
            self.refresh()
        # open all the pngs so we can save them to gif
        pngImages = [Image.open(fn) for fn in tmpPngNames]
        sleep_time = (1000.0 / self.opts.framerate) / 1000.0    # or 0.1 == good, too
        self.pngsToGif(filename, pngImages, sleep_time)
        for rmFile in tmpPngNames:
            os.remove(rmFile)
        return True

    def pngsToGif(self, outfile, pngImages, sleeptime):
        # create frames
        frames = []
        for frame in pngImages:
            frames.append(frame)
        # Save into a GIF file that loops forever
        frames[0].save(outfile, format='GIF',
               append_images=frames[1:],
               save_all=True,
               duration=sleeptime * 1000, loop=0)

    def showHelp(self):
        if self.appState.hasHelpFile:
            self.showAnimatedHelpScreen()
            self.showAnimatedHelpScreen(page=2)
        else:
            self.showStaticHelp()    

    def showStaticHelp(self):
        self.cursorOff()
        self.stdscr.nodelay(0)
        helpScreenText = '''
                  __                __
                _|  |__ __ _____ __|  |_____ _____ __ __ __
               / _  |  |  |   __|  _  |   __|  _  |  |  |  |\\
              /_____|_____|__|__|_____|__|___\\____|________| |  Durr....
              \\_____________________________________________\\|  v %s

      alt-k - next frame                  alt-' - delete current line
      alt-j - prev frame                  alt-/ - insert line
      alt-n - iNsert current frame clone  alt-, - delete current column.
      alt-N - appeNd empty frame          alt-. - insert new column
      alt-p - start/stop Playback         alt-c - Color picker (256 only)
      alt-d - Delete current frame        alt-m - Menu
      alt-D - set current frame Delay     F1-F10 - insert character
      alt-+/alt-- increase/decrease FPS   alt-z - undo
      alt-M - Move current frame          alt-r - Redo
      alt-up - next fg color              alt-s - Save
      alt-down - prev fg color            alt-o - Open
      alt-right - next bg color           alt-q - Quit
      alt-left - prev bg color            alt-h - Help
      alt-R - set playback/edit Range     alt-pgdn - next character set
      alt-g - Go to frame #               alt-pgup - prev character set

Help file could not be found. You might want to reinstsall Durdraw...
Can use ESC or META instead of ALT
''' % self.appState.durVer 
        # remove the blank first line from helpScreenText..
        # it's easier to edit here with the blank first line.
        helpScreenText = '\n'.join(helpScreenText.split('\n')[1:]) 
        self.clearStatusLine()
        self.addstr(0, 0, helpScreenText)
        self.promptPrint("* Press the ANY key (or click) to continue *")
        self.stdscr.getch()
        self.stdscr.clear()
        self.cursorOn()
        if self.playing == True:
            self.stdscr.nodelay(1)

    def hardRefresh(self):
        self.stdscr.redrawwin()
        self.stdscr.clear()
        self.refresh()

    def refresh(self):          # rename to redraw()?
        """Refresh the screen"""
        topLine = self.appState.topLine
        if self.appState.playingHelpScreen_2:
            mov = self.appState.helpMov_2
        elif self.appState.playingHelpScreen:
            mov = self.appState.helpMov
        else:
            mov = self.mov
        # Figure out the last line to draw
        lastLineToDraw = topLine + self.realmaxY - 2 # right above the status line
        if lastLineToDraw > mov.sizeY:
            lastLineToDraw = mov.sizeY
        screenLineNum = 0
        # Draw each character
        for linenum in range(topLine, lastLineToDraw):
            line = mov.currentFrame.content[linenum]
            for colnum in range(mov.sizeX):
                charColor = mov.currentFrame.newColorMap[linenum][colnum]
                try:
                    # set ncurss color pair
                    cursesColorPair = self.ansi.colorPairMap[tuple(charColor)] 
                except: # Or if we can't, fail to the terminal's default color
                    cursesColorPair = 0
                if charColor[0] > 8 and charColor[0] < 16 and self.appState.colorMode == "16":    # bright color
                    self.addstr(screenLineNum, colnum, str(line[colnum]), curses.color_pair(cursesColorPair) | curses.A_BOLD)
                else:
                    self.addstr(screenLineNum, colnum, str(line[colnum]), curses.color_pair(cursesColorPair))
            # draw border on right edge of line
            if self.appState.drawBorders:
                self.addstr(screenLineNum, mov.sizeX, ":", curses.color_pair(self.appState.theme['borderColor']))
            screenLineNum += 1
        # draw bottom border
        if self.appState.drawBorders and screenLineNum < self.realmaxY - 3 :
            self.addstr(screenLineNum, 0, "." * mov.sizeX, curses.color_pair(self.appState.theme['borderColor']))
            self.addstr(screenLineNum, mov.sizeX, ":", curses.color_pair(self.appState.theme['borderColor']))
        else:
            pass
        for x in range(screenLineNum, mov.sizeY):
            self.addstr(x, 0, " " * mov.sizeX)
        curses.panel.update_panels()
        self.stdscr.refresh()

    def addColToCanvas(self):
        self.undo.push()    # window is big enough
        for frameNum in range(0, len(self.mov.frames)):
            for x in range(len(self.mov.frames[frameNum].content)):
                self.mov.frames[frameNum].content[x].insert(self.xy[1] - 1, ' ')
                self.mov.frames[frameNum].newColorMap[x].insert(self.xy[1] - 1, [1,0])
        self.mov.sizeX += 1
        self.opts.sizeX += 1

    def delColFromCanvas(self):
        if self.mov.sizeX > 1 and self.xy[1] != self.mov.sizeX:
            self.undo.push()
            for frameNum in range(0, len(self.mov.frames)):     # Pop current column from every
                for x in range(len(self.mov.frames[frameNum].content)):     # line
                    self.mov.frames[frameNum].content[x].pop(self.xy[1] - 1)
                    self.mov.frames[frameNum].newColorMap[x].pop(self.xy[1] - 1)
            self.mov.sizeX -= 1
            self.opts.sizeX -= 1
            self.hardRefresh()

    def addLineToCanvas(self):
        self.undo.push()
        for frameNum in range(0, len(self.mov.frames)):
            self.mov.frames[frameNum].content.insert(self.xy[0] + 1, list(' ' * self.mov.sizeX))
            self.mov.frames[frameNum].newColorMap.insert(self.xy[0] + 1, [[1,0]] * self.mov.sizeX)
        self.mov.sizeY += 1
        self.opts.sizeY += 1

    def delLineFromCanvas(self):
        if self.mov.sizeY > 1 and self.xy[0] != self.mov.sizeY - 1:
            self.undo.push()
            for frameNum in range(0, len(self.mov.frames)):
                self.mov.frames[frameNum].content.pop(self.xy[0])
                self.mov.frames[frameNum].newColorMap.pop(self.xy[0])
            self.mov.sizeY -= 1
            self.opts.sizeY -= 1
            self.hardRefresh()

    def addCol(self, frange=None):
        """Insert column at position of cursor"""
        self.undo.push()
        if frange:  # framge range
            for frameNum in range(frange[0] - 1, frange[1]):
                for x in range(len(self.mov.frames[frameNum].content)):
                    self.mov.frames[frameNum].content[x].insert(self.xy[1] - 1, ' ')
                    self.mov.frames[frameNum].content[x].pop()
                    self.mov.frames[frameNum].newColorMap[x].insert(self.xy[1] - 1, [1,0])
                    self.mov.frames[frameNum].newColorMap[x].pop()
        else:
            for x in range(len(self.mov.currentFrame.content)):
                self.mov.currentFrame.content[x].insert(self.xy[1] - 1, ' ')
                self.mov.currentFrame.content[x].pop()
                self.mov.currentFrame.newColorMap[x].insert(self.xy[1] - 1, [1,0])
                self.mov.currentFrame.newColorMap[x].pop()
        # insert bit here to shift color map to the right from the column
        # onward. how: start at top right character, work down to bottom 
        # copying the color from the character to the left.
        # Then move left a column and repeat, etc, until you're at self.xy[1] -1 :).
        self.refresh()

    def delCol(self, frange=None):
        """Erase column at position of cursor"""
        self.undo.push()
        if frange:  # framge range
            for frameNum in range(frange[0] - 1, frange[1]):
                for x in range(len(self.mov.frames[frameNum].content)):     # Pop current column from every
                    self.mov.frames[frameNum].content[x].pop(self.xy[1] - 1)     # line & add a blank
                    self.mov.frames[frameNum].content[x].append(' ')         # at the end of each line.
                    self.mov.frames[frameNum].newColorMap[x].pop(self.xy[1] - 1)     # line & add a blank
                    self.mov.frames[frameNum].newColorMap[x].append([1,0])         # at the end of each line.
        else:
            for x in range(len(self.mov.currentFrame.content)):         # Pop current column from every
                self.mov.currentFrame.content[x].pop(self.xy[1] - 1)     # line & add a blank
                self.mov.currentFrame.content[x].append(' ')         # at the end of each line.
                self.mov.currentFrame.newColorMap[x].pop(self.xy[1] - 1)     # line & add a blank
                self.mov.currentFrame.newColorMap[x].append([1,0])         # at the end of each line.
        self.refresh()

    def delLine(self, frange=None):
        """delete current line""" 
        self.undo.push()
        if frange:
            for frameNum in range(frange[0] - 1, frange[1]):
                self.mov.frames[frameNum].content.pop(self.xy[0])
                self.mov.frames[frameNum].content.append([])
                self.mov.frames[frameNum].content[len(self.mov.frames[frameNum].content) - 1] = list(' ' * self.mov.sizeX)
                self.mov.frames[frameNum].newColorMap.pop(self.xy[0])
                self.mov.frames[frameNum].newColorMap.append([])
                self.mov.frames[frameNum].newColorMap[len(self.mov.frames[frameNum].newColorMap) - 1] = [[1,0]] * self.mov.sizeX
        else:
            self.mov.currentFrame.content.pop(self.xy[0])
            self.mov.currentFrame.content.append([])
            self.mov.currentFrame.content[len(self.mov.currentFrame.content) - 1] = list(' ' * self.mov.sizeX)
            self.mov.currentFrame.newColorMap.pop(self.xy[0])
            self.mov.currentFrame.newColorMap.append([])
            self.mov.currentFrame.newColorMap[len(self.mov.currentFrame.newColorMap) - 1] = [[1,0]] * self.mov.sizeX
        self.refresh()

    def addLine(self, frange=None):
        """Insert new line"""   
        self.undo.push()
        if frange:
            for frameNum in range(frange[0] - 1, frange[1]):
                self.mov.frames[frameNum].content.insert(self.xy[0], list(' ' * self.mov.sizeX))
                self.mov.frames[frameNum].content.pop()
                self.mov.frames[frameNum].newColorMap.insert(self.xy[0], [[1,0]] * self.mov.sizeX)
                self.mov.frames[frameNum].newColorMap.pop()
                self.refresh()
        else:
            self.mov.currentFrame.content.insert(self.xy[0], list(' ' * self.mov.sizeX))
            self.mov.currentFrame.content.pop()
            self.mov.currentFrame.newColorMap.insert(self.xy[0], [[1,0]] * self.mov.sizeX)
            self.mov.currentFrame.newColorMap.pop()
        self.refresh()

    def startSelecting(self, firstkey=None, mouse=False):   # firstkey is the key the user was
        #pressing. left, right, etc
        """Mark selection for copy/cut/move - trigger with shift-arrow-keys"""
        # any other key returns (cancels)
        # print message: "Select mode - Enter to select, Esc to cancel"
        startPoint =  [self.xy[0],  self.xy[1]]   # set to wherever the cursor is
        endPoint = startPoint
        selecting = True
        self.stdscr.nodelay(0)  # wait for getch input
        c = firstkey
        while selecting:
            self.clearStatusBar()
            endPoint =  [self.xy[0],  self.xy[1]]   # set to wherever the cursor is
            self.addstr(self.statusBarLineNum, 0, f"Use arrow keys to make selection, enter when done.")
            self.refresh()
            # draw block area on top of drawing area
            mov = self.mov
            if endPoint[0] >= startPoint[0]:    # if we're moving right of start point
                firstLineNum = startPoint[0]
                lastLineNum = endPoint[0]
            else:   # otherwise, we're moving left
                lastLineNum = startPoint[0]
                firstLineNum = endPoint[0]
            if endPoint[1] >= startPoint[1]:    # we're moving down from start point
                firstColNum = startPoint[1]
                lastColNum = endPoint[1]
            else:   # we're moving up from start point
                lastColNum = startPoint[1]
                firstColNum = endPoint[1]
            # draw selected area inverse
            for linenum in range(firstLineNum, lastLineNum + 1):
                for colnum in range(firstColNum - 1, lastColNum):
                    if colnum == self.mov.sizeX - 1:   # prevent overflow on last line
                        colnum -= 1
                    charColor = mov.currentFrame.newColorMap[linenum][colnum]
                    try: # set ncurss color pair
                        cursesColorPair = self.ansi.colorPairMap[tuple(charColor)] 
                    except: # Or if we can't, fail to the terminal's default color
                        cursesColorPair = 0
                    self.addstr(linenum - self.appState.topLine, colnum, mov.currentFrame.content[linenum][colnum], curses.color_pair(cursesColorPair) | curses.A_REVERSE)
            width = lastColNum - firstColNum + 1
            height = lastLineNum - firstLineNum + 1
            # end draw block area
            self.stdscr.redrawwin()
            c = self.stdscr.getch()
            if c in [98, curses.KEY_LEFT, curses.KEY_SLEFT]:
                self.move_cursor_left()
            elif c in [98, curses.KEY_RIGHT, curses.KEY_SRIGHT]:
                self.move_cursor_right()
            # 337 and 520 - shift-up, 336 and 513 = shift-down
            elif c in [339, curses.KEY_PPAGE]:  # page up
                self.move_cursor_pgup()
            elif c in [338, curses.KEY_NPAGE]:  # page down
                self.move_cursor_pgdown()
            elif c in [98, curses.KEY_UP, 337, 520]:
                self.move_cursor_up()
            elif c in [98, curses.KEY_DOWN, 336, 513]:
                self.move_cursor_down()
            elif c in [339, curses.KEY_HOME]:  # 339 = home
                self.xy[1] = 1
            elif c in [338, curses.KEY_END]:   # 338 = end
                self.xy[1] = self.mov.sizeX - 1
            elif c in [13, curses.KEY_ENTER]:
                # Ask user what operation they want, and then do it on the selected area
                # copy, cut, fill, or copy into all frames :)
                prompting = True
                self.addstr(self.statusBarLineNum, 0, " " * self.mov.sizeX) # clear status bar
                self.promptPrint("[C]opy to clipboard, [D]elete, or Copy to [A]ll Frames in playback range? " )
                while prompting:
                    prompt_ch = self.stdscr.getch()
                    if chr(prompt_ch) in ['c', 'C']:    # Copy
                        self.copySegmentToClipboard([firstLineNum, firstColNum], height, width)
                        prompting = False
                    #if chr(prompt_ch) in ['m', 'M']:    # move
                    #    prompting = False
                    if chr(prompt_ch) in ['d', 'D']:    # delete/clear
                        self.promptPrint("Delete across all frames in playback range (Y/N)? ")
                        askingAboutRange = True
                        while askingAboutRange:
                            prompt_ch = self.stdscr.getch()
                            if chr(prompt_ch) in ['y', 'Y']:    # yes, all range
                                self.deleteSegment([firstLineNum, firstColNum], height, width, frange=self.appState.playbackRange)
                                askingAboutRange = False
                            if chr(prompt_ch) in ['n', 'N']:    # yes, all range
                                self.deleteSegment([firstLineNum, firstColNum], height, width)
                                askingAboutRange = False
                            elif prompt_ch == 27:  # esc, cancel
                                askingAboutRange = False
                        prompting = False
                    if chr(prompt_ch) in ['a', 'A']:    # copy to all frames
                        self.copySegmentToAllFrames([firstLineNum, firstColNum], height, width, frange=self.appState.playbackRange)
                        prompting = False
                    elif prompt_ch == 27:  # esc, cancel
                        prompting = False
                selecting = False
            elif c == curses.KEY_MOUSE: # Remember, we are playing here
                try:
                    _, mouseX, mouseY, _, mouseState = curses.getmouse()
                except:
                    pass
                realmaxY,realmaxX = self.realstdscr.getmaxyx()
                # enable mouse tracking only when the button is pressed
                if mouseState == curses.BUTTON1_CLICKED or mouseState & curses.BUTTON_SHIFT:
                    if mouseY < self.mov.sizeY and mouseX < self.mov.sizeX: # in edit area
                        self.xy[1] = mouseX + 1 # set cursor position
                        self.xy[0] = mouseY
                            

            elif c == 27:   # esc
                selecting = False
        if self.playing:
            self.stdscr.nodelay(1)
        else:
            self.stdscr.nodelay(0)

    def pasteFromClipboard(self, startPoint=None, clipBuffer=None, frange=None):
        if not clipBuffer:
            clipBuffer = self.clipBoard
        if not clipBuffer:  # clipboard is empty, and no buffer provided
            return False
        self.undo.push()
        if not startPoint:
            startPoint = self.xy
        lineNum = 0
        colNum = 0
        width = len(clipBuffer.content) - 1
        height = len(clipBuffer.content[0]) - 1
        for lineNum in range(0, height):
            for colNum in range(0, width):
                charColumn = startPoint[1] + colNum
                charLine = startPoint[0] + lineNum
                character = ord(clipBuffer.content[colNum][lineNum])    
                cursesColorPair = clipBuffer.newColorMap[colNum][lineNum]
                charFg = cursesColorPair[0]
                charBg = cursesColorPair[1]
                if charColumn < self.mov.sizeX + 1 and charLine < self.mov.sizeY:
                    if not frange:
                        self.insertChar(character, fg=charFg, bg=charBg, x=charColumn, y=charLine, pushUndo=False)
                    else:
                        self.insertChar(character, fg=charFg, bg=charBg, x=charColumn, y=charLine, pushUndo=False, frange=frange)

    def copySegmentToClipboard(self, startPoint, height, width):
        """ startPoint is [line, column] """
        clipBoard = self.copySegmentToBuffer(startPoint, height, width)
        self.clipBoard = clipBoard

    def copySegmentToAllFrames(self, startPoint, height, width, frange=None):
        tempFrame = self.copySegmentToBuffer(startPoint, height, width)
        # paste into each frame in range, at startPoint
        self.pasteFromClipboard(clipBuffer=tempFrame, startPoint=startPoint, frange=frange)

    def copySegmentToBuffer(self, startPoint, height, width):
        # Return a buffer, aka a frame or movie object
        # Buffer can be put into clipboard, or used to move
        # around screen, e, etc.

        firstLineNum = startPoint[0]
        firstColNum = startPoint[1]
        lastLineNum = firstLineNum + height
        lastColNum = firstColNum + width

        # Make a buffer for characters and color pairs big enough to store the
        # copied image segment.
        # This can be done by making a frame.
        bufferFrame = durmovie.Frame(height + 1, width + 1)

        newLineNum = 0
        newColNum = 0
        # For each character in the selection...
        for linenum in range(firstLineNum, lastLineNum):
            for colnum in range(firstColNum - 1, lastColNum - 1):
                # copy color from movie into buffer
                charColor = self.mov.currentFrame.newColorMap[linenum][colnum]
                try:
                    bufferFrame.newColorMap[newColNum][newLineNum] = charColor
                except Exception as E:
                    print(f"Exception: {str(E)}")
                    pdb.set_trace()
                # copy character from movie into buffer
                output_char = self.mov.currentFrame.content[linenum][colnum]
                try:
                    bufferFrame.content[newColNum][newLineNum] = output_char
                except Exception as E:
                    print(f"Exception: {str(E)}")
                    pdb.set_trace()
                newColNum += 1
            newLineNum += 1
            newColNum = 0
        return bufferFrame

    def deleteSegment(self, startPoint, height, width, frange=None):
        """ Delete everyting in the current frame, or framge range """
        for lineNum in range(0, height):
            for colNum in range(0, width):
                charColumn = startPoint[1] + colNum
                charLine = startPoint[0] + lineNum
                character = ord(" ")
                charFg = 1
                charBg = 0
                if charColumn < self.mov.sizeX + 1 and charLine < self.mov.sizeY:
                    if not frange:
                        self.insertChar(character, fg=charFg, bg=charBg, x=charColumn, y=charLine, pushUndo=False)
                    else:
                        self.insertChar(character, fg=charFg, bg=charBg, x=charColumn, y=charLine, pushUndo=False, frange=frange)

    def clearStatusBarNoRefresh(self):
        self.addstr(self.statusBarLineNum, 0, " " * self.mov.sizeX) # clear lower status bar
        self.addstr(self.statusBarLineNum + 1, 0, " " * self.mov.sizeX) # clear upper status bar

   
    def clearStatusBar(self):
        self.addstr(self.statusBarLineNum, 0, " " * self.mov.sizeX) # clear lower status bar
        self.addstr(self.statusBarLineNum + 1, 0, " " * self.mov.sizeX) # clear upper status bar
        self.refresh()
 
    def parseArgs(self):
        """ do argparse stuff, get filename from user """
        pass

