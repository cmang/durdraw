# Stuff to draw widgets, status bars, etc. The logical parts, separate from
# the drawing/ncurses part. 
# For example, in the status bar, we have a color swatches widget.
# The color swatch widget should know everything about itself except curses.
# NO CURSES CODE IN THIS FILE!!!!
# Instead make a durdraw_ui_widgets_curses that handles the curses bits. Then do the same with kivy, etc.
# # it should know its location inside of the Status Bar

import pdb
import time

from durdraw.durdraw_ui_widgets_curses import ButtonHandler
from durdraw.durdraw_ui_widgets_curses import ColorPickerHandler
from durdraw.durdraw_ui_widgets_curses import ColorSwatchHandler
from durdraw.durdraw_ui_widgets_curses import DrawCharPickerHandler
from durdraw.durdraw_ui_widgets_curses import MenuHandler
from durdraw.durdraw_ui_widgets_curses import StatusBarHandler 
from durdraw.durdraw_ui_widgets_curses import FgBgColorPickerHandler
from durdraw.durdraw_gui_manager import Gui

class Button():
    def __init__(self, label, x, y, callback, window, invisible = False, appState=None):
        #self.location = 0;  # 0 = beginning of /tring
        self.x = x
        self.y = y
        self.appState = appState
        self.realX = x
        self.realY = y
        self.label = label  # What you should click
        self.width = len(self.label)
        self.color = "brightGreen"  # bright green = clickable by defaulta
        self.image = None   # If we want an icon in a GUI version
        self.window = window    # stdscr in the case of screen
        self.callback = callback
        self.parameter = None
        self.hidden = False
        self.selected = False
        self.picker= False
        self.invisible = invisible # If true, responds to clicks but does not show. Useful for "overlays"
        self.handler = ButtonHandler(self, self.window, callback, appState=self.appState)

    def hide(self):
        self.hidden = True
        self.handler.hidden = True

    def show(self):
        self.hidden = False
        self.draw()

    def update_real_xy(self, x=None, y=None):
        if x == None:
            x = self.realX
        if y == None:
            y = self.realY
        self.realX = x
        self.realY = y

    def draw(self):
        should_draw = True
        if self.invisible:
            should_draw = False
        if self.hidden:
            should_draw = False
        if self.appState.playOnlyMode:
            should_draw = False
        if should_draw:
            self.handler.draw()

    def make_invisible(self):
        self.invisible = True

    def on_click(self):
        if self.hidden == False:
            self.selected = True
            self.handler.draw()
            self.handler.on_click()
            self.selected = False
            #self.handler.draw()

    def handle_event(self, event):
        return self.handler.handle_event(event)

class Menu():
    def __init__(self, window, x=0, y=0, caller=None, appState=None, statusBar=None):
        """ init menu items """ 
        self.window = window
        self.caller = caller
        self.appState=appState
        self.items = {}
        self.buttons = []
        self.hidden = True
        self.title = None
        self.statusBar = None
        self.x = x
        self.y = y
        self.handler = MenuHandler(self, window, appState=appState)
        self.gui = Gui(window=self.window)

    def set_x(self, x):
        self.x = x
        self.handler.x = x

    def set_y(self, y):
        self.y = y
        self.handler.y = y

    def set_title(self, title):
        self.title = title
        self.handler.title = self.title

    def add_item(self, label, on_click, hotkey):
        props = {"on_click": on_click, "hotkey": hotkey}
        item = {label: props}
        self.items.update(item)
        # add button
        #itemButton = Button(label, 0, 0, on_click, self.window)
        itemButton = Button(label, 0, self.x, on_click, self.window, appState=self.appState)
        itemButton.make_invisible()
        self.buttons.append(itemButton)
        #self.handler.rebuild()
        #itemButton.update_real_xy(x=self.caller.x)

    def show(self):
        for button in self.buttons:
            #button.x = self.x
            #button.update_real_xy(x=self.x)
            self.gui.add_button(button)
            button.show()
            #pdb.set_trace()
        self.hidden = False
        self.handler.show()

    def tryHotKey(self, key):
        """ Try a hotkey to see if it works """
        pass

    def hide(self):
        self.handler.hide()
        for button in self.buttons:
            self.gui.del_button(button)
        self.hidden = True

    def showHide(self):
        if self.hidden == True:
            self.show()
        else:
            self.hide()

class FgBgColorPicker:
    """ Draw the FG and BG color boxes that you can click on to launch a
    color selector """
    def __init__(self, window, x=0, y=0):
        self.window = window
        self.x = x
        self.y = y
        self.handler = FgBgColorPickerHandler(self, x=self.x, y=self.y)
    def draw(self):
        self.handler.draw()

class DrawCharPicker:
    """ Ask the user for the character to draw with """
    def __init__(self, window, x=0, y=0, caller=None):
        self.window = window
        self.caller = caller
        self.appState = self.caller.caller.appState
        self.handler = DrawCharPickerHandler(self, self.window)

    def pickChar(self):
        self.handler.pickChar()

class ColorPicker:
    """ Draw a color palette, let the user click a color.
    Makes the user's selected color available somewhere. """
    def __init__(self, window, x=0, y=0, caller=None):
        self.hidden = True
        self.window = window
        self.colorMap = {}
        self.x = x
        self.y = y
        self.caller = caller
        self.handler = ColorPickerHandler(self, window)

    def showHide(self):
        #pdb.set_trace()
        if self.hidden == True:
            self.hidden = False
            self.show()
        elif self.hidden == False:
            self.hidden = True
            self.hide()

    def show(self):
        self.hidden = False
        self.showFgPicker()

    def showFgPicker(self):
        """ Returns the color picked by the user
        """
        # Draw foreground colors 1-5 in a panel.
        # Run an input loop to let user use mouse or keyboard
        # to select color (arrows and return). Then return the
        # selected color.
        self.hidden = False
        color = self.handler.showFgPicker()
        self.hide()
        return color

    def hide(self):
        self.hidden = True
        self.handler.hide()

class MiniSelector():   # for seleting cursor mode
    """ Line up some characters beside each other, and let the user select
    which one by clicking on it. The currently selected one is drawn inverse.
    Example, for picking between Select, Draw and Color: SPC """
    def __init__(self):
        self.items = []

class ColorSwatch():
    def __init__(self, caller, x=0, y=0):
        """ Initialize a swatch of 24 colors
        """
        window = caller.window
        self.window = window
        self.handler = ColorSwatchHandler(self, self.window)
        self.bank = []
        self.colorMap = {}
        self.x = x
        self.y = y
        for color in range(0,24):
            self.bank.append(color)
        #swatch = [1] * 24   # color 1

    def draw(self):
        self.handler.draw()


class StatusBar():
    def __init__(self, caller, x=0, y=0, appState=None):
        window = caller.stdscr
        self.caller=caller
        self.appState = appState
        self.window = window
        self.gui = caller.gui   # top level gui handler thing
        self.handler = StatusBarHandler(self, window)
        self.items = []
        self.buttons = []
        self.colorPickerEnabled = False
        self.hidden = False
        self.x = x
        self.y = y
        # menu items 
        self.menuButton = None
        # Create a menu list item, add menu items to it
        mainMenu = Menu(self.window, x = self.x - 1, y = self.y, caller=self, appState=self.appState, statusBar=self)
        #mainMenu.gui = self.gui
        mainMenu.add_item("New", caller.clearCanvasPrompt, "n")
        mainMenu.add_item("Open", caller.openFromMenu, "o")
        mainMenu.add_item("Save", caller.save, "s")
        mainMenu.add_item("Help", caller.showHelp, "h")
        mainMenu.add_item("Quit", caller.safeQuit, "q")
        #menuButton = Button("?", 0, 0, mainMenu.showHide, self.window)
        menuButton = Button("Menu", 0, 0, mainMenu.showHide, self.window, appState=self.appState)
        self.menuButton = menuButton
        menuButton.realX = self.x + menuButton.x
        menuButton.realY = self.y + menuButton.y
        menuButton.show()
        self.menuButton = menuButton
        #mainMenu.x = menuButton.realX - 1
        #mainMenu.y = menuButton.realY
        mainMenu.set_x(menuButton.realX - 1)
        mainMenu.set_y(menuButton.realY)
        self.mainMenu = mainMenu

        toolMenu = Menu(self.window, x=45, y=self.y, caller=self, appState=self.appState, statusBar=self)
        toolMenu.set_title("Mouse Tools:")
        #toolMenu = Menu(self.window, x=5, y=self.y, caller=self)
        toolMenu.add_item("Move", self.setCursorModeSel, "m")
        toolMenu.add_item("Draw", self.setCursorModePnt, "d")
        toolMenu.add_item("Color", self.setCursorModeCol, "c")
        toolMenu.add_item("Erase", self.setCursorModeErase, "e")
        toolMenu.add_item("Eyedrop", self.setCursorModeEyedrop, "y")
        self.toolMenu = toolMenu
        # Make cursor tool selector button
        toolButton = Button("Tool", 0, 45, toolMenu.showHide, self.window, appState=self.appState)
        #toolButton = Button("Tool", 0, 5, toolMenu.showHide, self.window)
        toolButton.label = self.caller.appState.cursorMode
        toolButton.picker = True
        toolButton.realX = self.x + toolButton.x    # toolbar shit
        toolButton.realY = self.y + toolButton.y
        toolButton.show()
        toolMenu.set_x(toolButton.realX - 1)    # line up the menu above the button
        toolMenu.set_y(toolButton.realY)
        self.toolButton = toolButton

        charSetButton = Button("CharSet", 1, 26, caller.showCharSetPicker, self.window, appState=self.appState)
        # make proper label for character set button
        charSetLabel = self.caller.appState.characterSet
        if charSetLabel == "Unicode Block":
            charSetLabel = self.caller.appState.unicodeBlock
        charSetLabel = f"{charSetLabel[:3]}.."
        charSetButton.label = charSetLabel
        charSetButton.show()
        self.charSetButton = charSetButton

        drawCharPicker = DrawCharPicker(self.window, caller=self)
        drawCharPickerButton = Button(self.caller.appState.drawChar, 0,  51, drawCharPicker.pickChar, self.window, appState=self.appState)
        drawCharPickerButton.picker = True
        drawCharPickerButton.realX = self.x + drawCharPickerButton.x    # toolbar shit
        drawCharPickerButton.realY = self.y + drawCharPickerButton.y
        #drawCharPickerButton.show() 
        drawCharPickerButton.hide() 
        self.drawCharPickerButton = drawCharPickerButton


        colorPicker = ColorPicker(self.window, x=self.x - 2, y = self.y + 2, caller=caller)
        self.colorPicker = colorPicker

        if self.caller.appState.colorMode == "256":
            self.colorPickerButton = Button("FG:  ", 1, 0, colorPicker.showHide, self.window, appState=self.appState)
            self.colorPickerButton.invisible = True
            self.colorPickerButton.realX = self.x + self.colorPickerButton.x
            self.colorPickerButton.realY = self.y + self.colorPickerButton.y + 1
            self.colorPickerButton.show()
            self.items.append(self.colorPickerButton)
            self.buttons.append(self.colorPickerButton)
        #pdb.set_trace()
        #colorPicker.show()  # for testing

        #self.swatch = ColorSwatch(self, x=3, y=self.y)
        #self.swatch.colorMap = caller.ansi.colorPairMap
        
        # Figure out where in the status bar to put it
        newX = len(str(self.items))
        newY = self.y
        #fgBgColors = FgBgColorPicker(self.window, x=newX, y=newY)
        #menuButton.addItem(label="Help!", type="link", callback=None)
        # Initialize individual buttons and items
        #startButton = Button(label="!", callback=self.draw_start_menu)
        self.items.append(menuButton)
        self.items.append(toolButton)
        self.items.append(drawCharPickerButton)
        self.items.append(charSetButton)
        #self.items.append(fgBgColors)
        #self.items.append(self.swatch)
        self.buttons.append(menuButton)
        self.buttons.append(toolButton)
        self.buttons.append(drawCharPickerButton)
        self.buttons.append(charSetButton)
        # Add them to the items

    def hide(self):
        self.hidden = True
        for item in self.items:
            item.hide()
        for item in self.buttons:
            item.hide()

    def show(self):
        self.hidden = False
        for item in self.items:
            item.show()
        for item in self.buttons:
            item.show()

    def enableColorPicker(self):
        pass

    def disableColorPicker(self):
        pass

    def setCursorModeSel(self):
        self.caller.appState.setCursorModeSel()
        self.toolButton.label = self.caller.appState.cursorMode
        self.drawCharPickerButton.hide()

    def setCursorModePnt(self):
        self.caller.appState.setCursorModePnt()
        self.toolButton.label = self.caller.appState.cursorMode
        self.drawCharPickerButton.show()

    def setCursorModeCol(self):
        self.caller.appState.setCursorModeCol()
        self.toolButton.label = self.caller.appState.cursorMode
        self.drawCharPickerButton.hide()

    def setCursorModeErase(self):
        self.caller.appState.setCursorModeErase()
        self.toolButton.label = self.caller.appState.cursorMode
        self.drawCharPickerButton.hide()

    def setCursorModeEyedrop(self):
        self.caller.appState.setCursorModeEyedrop()
        self.toolButton.label = self.caller.appState.cursorMode
        self.drawCharPickerButton.hide()

    def updateLocation(self, x, y):
        self.x = x
        self.y = y

    def draw(self):
        """ Draw the status bar """
        if self.hidden:
            return False
        self.handler.draw()
        for item in self.items:
            if item.hidden is False:
                item.handler.draw(plusX=self.x, plusY=self.y)




