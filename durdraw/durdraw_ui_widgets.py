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
from durdraw.durdraw_ui_widgets_curses import ToolTipHandler
from durdraw.durdraw_gui_manager import Gui

class Button():
    def __init__(self, label, x, y, callback, window, invisible = False, appState=None):
        #self.location = 0;  # 0 = beginning of /tring
        self.x :int = x
        self.y :int = y
        self.appState = appState
        self.realX :int = x
        self.realY :int = y
        self.label :str = label  # What you should click
        self.identity :str = label   # Unique from the label
        self.tooltip_command :str = None
        self.tooltip_hidden :bool = True
        self.persistant_tooltip :bool = False
        self.width :int = len(self.label)
        self.color :str = "brightGreen"  # bright green = clickable by defaulta
        self.image = None   # If we want an icon in a GUI version
        self.window = window    # stdscr in the case of screen
        self.callback = callback
        # sub_buttons automatically show and hide with this
        # button. like satellites.
        #
        # {my-label: sub-button-pointer}
        # The idea is that when the label is "Draw" and I run .show(),
        # call sub-button.show().
        self.sub_buttons = {}
        self.parameter = None
        self.hidden :bool = False
        self.enabled = True     # Responds to clicks
        self.selected :bool = False
        self.picker :bool = False
        self.invisible :bool = invisible # If true, responds to clicks but does not show. Useful for "overlays"
        self.handler = ButtonHandler(self, self.window, callback, appState=self.appState)

    def add_sub_button(self, label, button):
        """ Label is what self.label should be when I should
            calll button.show() """
        self.sub_buttons.update({label: button})

    def set_tooltip_command(self, command: str):
        """ Command should be the keyboard command, like the "o" in esc-o """
        self.tooltip_command = command

    def get_tooltip_command(self):
        return self.tooltip_command

    def set_label(self, label):
        self.label = label 
        self.width = len(self.label)

    def hide(self):
        self.hidden = True
        #self.handler.hidden = True
        for label in self.sub_buttons:
            self.sub_buttons[label].hide()
        self.handler.hide()

    def show(self):
        self.hidden = False
        for label in self.sub_buttons:
            if self.label == label:
                self.sub_buttons[label].show()
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

    def become_selected(self):
        self.selected = True
        self.handler.draw()
        self.selected = False

    def on_click(self):
        #result = self.do_nothing()
        result = None
        #if self.hidden == False:
        if self.enabled and not self.hidden:
            self.selected = True
            self.handler.draw()
            result = self.handler.on_click()
            self.selected = False
        return result

    def do_nothing(self):
        pass

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
        self.is_submenu = False
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

    def add_item(self, label, on_click, hotkey, shortcut=None, has_submenu=False):
        props = {"on_click": on_click, "hotkey": hotkey, "shortcut": shortcut, "has_submenu": has_submenu}
        item = {label: props}
        self.items.update(item)
        # add button
        #itemButton = Button(label, 0, 0, on_click, self.window)
        if shortcut:
            long_label = f"{label} {shortcut}"
        else:
            long_label = f"{label} poop"
        itemButton = Button(long_label, 0, self.x, on_click, self.window, appState=self.appState)
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
        response = self.handler.show()
        return response

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
            return self.show()
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
    def __init__(self, window, x=0, y=0, caller=None, colorMode="256", type="fg"):
        self.hidden = True
        self.window = window
        self.colorMap = {}
        self.colorMode = colorMode
        self.type = type    # "fg" or "bg," or maybe "fgbg"
        self.x = x
        self.y = y
        self.totalColors = 256
        self.appState = caller.appState
        if colorMode == "256":
            self.height = 8
            self.width = 38
            self.totalColors = 255
        elif colorMode == "16":
            #self.height = 1
            #self.width = 16

            # short and wide - good
            self.height = 2
            self.width = 10

            # tall and thin - good, but color order
            # is wrong
         #self.height = 10
            #self.width = 4
            
            self.totalColors = 16
            if self.appState.iceColors:
                self.totalColors = 15
        self.caller = caller
        self.handler = ColorPickerHandler(self, window, width=self.width, height=self.height)

    def showHide(self):
        #pdb.set_trace()
        if self.hidden == True:
            self.hidden = False
            self.caller.appState.colorPickerSelected = True
            self.show()
        elif self.hidden == False:
            self.hidden = True
            self.caller.appState.colorPickerSelected = False
            self.hide()

    def switchTo(self):
        """ Switch user interaction to the color picker,
            already on the screen """
        self.caller.appState.colorPickerSelected = True
        self.showFgPicker()

    def show(self):
        self.hidden = False
        #self.showFgPicker()
        self.handler.show()

    def showFgPicker(self, message=None):
        """ Returns the color picked by the user
        """
        # Draw foreground colors 1-5 in a panel.
        # Run an input loop to let user use mouse or keyboard
        # to select color (arrows and return). Then return the
        # selected color.
        self.hidden = False
        color = self.handler.showFgPicker(message=message)
        if not self.caller.appState.sideBarShowing:
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


class ToolTipsGroup():
    """ These are tooltips that can show up without being
        tied to any specific object, other than an x/y location """
    def __init__(self, caller):
        self.tips = []
        self.hidden = True
        self.caller = caller

    def add_tip(self, hotkey :str, row=0, col=0):
        newTip = ToolTip(self.caller)
        newTip.hotkey = hotkey
        newTip.row = row
        newTip.column = col
        self.tips.append(newTip)

    def get_tip(self, hotkey :str):
        for tip in self.tips:
            if tip.hotkey == hotkey:
                return tip
        return False

    def show(self):
        self.hidden = False
        for tip in self.tips:
            tip.show()

    def hide(self):
        self.hidden = True
        for tip in self.tips:
            tip.hide()

class ToolTip():
    def __init__(self, context):
        # context is the caller, basically the statusbar
        # context provides window, appState, etc
        self.hotkey = '' # the key the user presses
        self.column = 0  # on the screen
        self.row = 0
        self.hidden = True
        self.alwaysHidden = False
        self.handler = ToolTipHandler(self, context)

    def set_hotkey(self, hotkey :str):
        self.hotkey = hotkey

    def set_location(self, row=None, column=None):
        if row == None:
            row = self.row
        if column == None:
            column = self.column
        self.row = row
        self.column = column

    def show(self):
        if not self.alwaysHidden:
            self.hidden = False
            self.handler.show()

    def hide(self):
        self.hidden = True
        self.handler.hide()

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

        # Initialize tooltips that aren't tied to a button object
        # These show up when the user hits esc, along with the
        # visible buttons' tooltips.
        # "Free floating tips"
        self.other_tooltips = ToolTipsGroup(self)
        self.other_tooltips.add_tip("g", row=0, col=7) # Frame
        self.other_tooltips.add_tip("+", row=0, col=7) # FPS+
        self.other_tooltips.add_tip("-", row=0, col=7) # FPS-
        self.other_tooltips.add_tip("D", row=0, col=7) # Frame delay
        self.other_tooltips.add_tip("R", row=0, col=7) # Frame range
        self.other_tooltips.add_tip("c", row=0, col=7) # color picker
        self.other_tooltips.add_tip("[", row=0, col=7) # prev charset
        self.other_tooltips.add_tip("]", row=0, col=7) # next charset
        self.other_tooltips.add_tip("p", row=0, col=7) # play/pause
        self.other_tooltips.add_tip("j", row=0, col=7) # prev frame
        self.other_tooltips.add_tip("k", row=0, col=7) # next frame

        # If we're in 16 color mode, always hide the "c" button
        if self.appState.colorMode == "16":
            colorPicker_tooltip = self.other_tooltips.get_tip('c')
            colorPicker_tooltip.alwaysHidden = True

        # Settings menu
        #settingsMenuColumn = mainMenu.handler.width # Try to place to the right of the main menu
        settingsMenuColumn = 24 # Try to place to the right of the main menu
        settingsMenu = Menu(self.window, x = self.x - 2, y = settingsMenuColumn, caller=self, appState=self.appState, statusBar=self)
        settingsMenu.add_item("16 Color Mode", caller.switchTo16ColorMode, "1")
        settingsMenu.add_item("256 Color Mode", caller.switchTo256ColorMode, "2")
        settingsMenu.add_item("VGA Colors", caller.enableTrueVGAColors, "v")
        settingsMenu.add_item("ZX Spectrum Colors", caller.enableTrueSpeccyColors, "z")
        settingsMenu.add_item("C64 Colors", caller.enableTrueC64Colors, "c")
        #settingsMenu.add_item("Deafult Colors", caller.resetColorsToDefault, "d")
        settingsMenu.add_item("Toggle Mouse", caller.toggleMouse, "m")
        settingsMenu.add_item("Toggle Color Scroll", caller.toggleColorScrolling, "s")
        settingsMenu.add_item("Toggle Wide Wrapping", caller.toggleWideWrapping, "w")
        if self.appState.mental:    # Experimental stuff
            settingsMenu.add_item("Toggle iCE Colors (MENTAL)", caller.toggleIceColors, "i")
            settingsMenu.add_item("Toggle Injecting (MENTAL)", caller.toggleInjecting, "j")
        if self.appState.debug:
            settingsMenu.add_item("Toggle Debug", caller.toggleDebug, "d")
            settingsMenu.add_item("Python Console", caller.jumpToPythonConsole, "p")
        settingsMenu.is_submenu = True
        #settingsMenu.add_item("Show/Hide Sidebar", caller.toggleSideBar, "s")
        settingsMenu.set_x(self.x - 1)
        settingsMenu.set_y(settingsMenuColumn)
        self.settingsMenu = settingsMenu

        # Transforms menu
        #transformMenuColumn = 24 # Try to place to the right of the main menu
        transformMenuColumn = 35 # Try to place to the right of the Animation menu
        transformMenu = Menu(self.window, x = self.x - 2, y = transformMenuColumn, caller=self, appState=self.appState, statusBar=self)
        transformMenu.add_item("Bounce", caller.transform_bounce, "b")
        transformMenu.add_item("Repeat", caller.transform_repeat, "r")
        transformMenu.add_item("Reverse", caller.transform_reverse, "v")
        transformMenu.add_item("Apply NeoFetch Keys", caller.apply_neofetch_keys, "n")
        #transformMenu.add_item("Show/Hide Sidebar", caller.toggleSideBar, "s")
        transformMenu.set_x(self.x - 1)
        transformMenu.set_y(transformMenuColumn)
        transformMenu.is_submenu = True
        self.transformMenu = transformMenu

        # main menu items 
        self.menuButton = None
        # Create a menu list item, add menu items to it
        mainMenu = Menu(self.window, x = self.x - 1, y = self.y, caller=self, appState=self.appState, statusBar=self)
        #mainMenu.gui = self.gui
        mainMenu.add_item("New/Clear", caller.clearCanvasPrompt, "n", shortcut="esc-C")
        mainMenu.add_item("Open", caller.openFromMenu, "o", shortcut="esc-o")
        mainMenu.add_item("Save", caller.save, "s", shortcut="esc-s")
        mainMenu.add_item("Undo", caller.clickedUndo, "u", shortcut="esc-z")
        mainMenu.add_item("Redo", caller.clickedRedo, "r", shortcut="esc-r")
        mainMenu.add_item("Mark/Select", caller.startSelecting, "k", shortcut="esc-K")
        mainMenu.add_item("Paste", caller.pasteFromMenu, "p", shortcut="esc-v")
        #mainMenu.add_item("16 Color Mode", caller.switchTo16ColorMode, "1")
        #mainMenu.add_item("256 Color Mode", caller.switchTo256ColorMode, "2")
        #mainMenu.add_item("Settings", settingsMenu.showHide, "t", has_submenu=True)
        mainMenu.add_item("Character Sets", caller.showCharSetPicker, "c", shortcut="esc-S")
        #mainMenu.add_item("Transform", caller.showTransformer, "a", has_submenu=True)
        mainMenu.add_item("Info/Sauce", caller.clickedInfoButton, "i", shortcut="esc-i")
        mainMenu.add_item("Color Picker", caller.selectColorPicker, "l", shortcut="tab")
        mainMenu.add_item("Viewer Mode", caller.enterViewMode, "v", shortcut="esc-V")
        mainMenu.add_item("Find /", caller.searchForStringPrompt, "/", shortcut="esc-F")
        mainMenu.add_item("Replace Color", caller.replaceColorUnderCursor, "e", shortcut="esc-L")
        mainMenu.add_item("Settings", caller.openSettingsMenu, "t", has_submenu=True)
        mainMenu.add_item("Help", caller.showHelp, "h", shortcut="esc-h")
        mainMenu.add_item("Quit", caller.safeQuit, "q", shortcut="esc-q")
        #menuButton = Button("?", 0, 0, mainMenu.showHide, self.window)
        #menuButton = Button("Menu", 0, 0, mainMenu.showHide, self.window, appState=self.appState)
        menuButton = Button("Menu", 0, 0, caller.openMainMenu, self.window, appState=self.appState)
        menuButton.set_tooltip_command('m')
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


        # Animation menu
        self.animButton = None
        #animButton_offset = 18
        animButton_offset = 7
        # Create a menu list item, add menu items to it
        animMenu = Menu(self.window, x = animButton_offset, y = self.y, caller=self, appState=self.appState, statusBar=self)
        animMenu.set_title("Animation:")
        animMenu.add_item("Clone Frame", caller.cloneToNewFrame, "n", shortcut="esc-n")
        animMenu.add_item("Append Empty Frame", caller.appendEmptyFrame, "a", shortcut="esc-N")
        animMenu.add_item("Delete Frame", caller.deleteCurrentFrame, "d", shortcut="esc-d")
        animMenu.add_item("Set Frame Delay", caller.getDelayValue, "l", shortcut="esc-D")
        animMenu.add_item("Set Playback Range", caller.getPlaybackRange, "r", shortcut="esc-R")
        animMenu.add_item("Go to Frame", caller.gotoFrameGetInput, "g", shortcut="esc-g")
        animMenu.add_item("Move Frame", caller.moveCurrentFrame, "m", shortcut="esc-M")
        animMenu.add_item("Shift Frames Right", caller.shiftMovieRight, "}", shortcut="esc-}")
        animMenu.add_item("Shift Frames Left", caller.shiftMovieLeft, "{", shortcut="esc-{")
        animMenu.add_item("Transform", caller.openTransformMenu, "t", has_submenu=True)
        animButton = Button("Anim", 0, animButton_offset, caller.openAnimMenu, self.window, appState=self.appState)
        animButton.set_tooltip_command('a')
        self.animButton = animButton
        animButton.realX = self.x + animButton.x
        animButton.realY = self.y + animButton.y
        animButton.show()
        self.animButton = animButton
        animMenu.set_x(animButton.realX - 1)
        animMenu.set_y(animButton.realY)
        self.animMenu = animMenu


        # Mouse tools menu
        toolMenu = Menu(self.window, x=45, y=self.y, caller=self, appState=self.appState, statusBar=self)
        toolMenu.set_title("Mouse Tools:")
        #toolMenu = Menu(self.window, x=5, y=self.y, caller=self)
        toolMenu.add_item("Move", self.setCursorModeMove, "m")
        #toolMenu.add_item("Select", self.setCursorModeSelect, "s")
        toolMenu.add_item("Draw", self.setCursorModeDraw, "d")
        toolMenu.add_item("Paint", caller.setCursorModePaint, "p")
        toolMenu.add_item("Color", self.setCursorModeCol, "c")
        toolMenu.add_item("Erase", self.setCursorModeErase, "e")
        toolMenu.add_item("Eyedrop", self.setCursorModeEyedrop, "y")
        toolMenu.add_item("Draw/Fill Char", caller.openDrawCharPicker, "h")
        self.toolMenu = toolMenu

        # Make cursor tool selector button
        # offset is how far right to put the button in the statusbar:
        #toolButton_offset = 45  
        #toolButton_offset = 7
        toolButton_offset = 14
        #toolButton = Button("Tool", 0, toolButton_offset, toolMenu.showHide, self.window, appState=self.appState)
        toolButton = Button("Tool", 0, toolButton_offset, caller.openMouseToolsMenu, self.window, appState=self.appState)
        #toolButton = Button("Tool", 0, 5, toolMenu.showHide, self.window)
        #toolButton.label = self.caller.appState.cursorMode
        toolButton.set_label(self.caller.appState.cursorMode)
        toolButton.set_tooltip_command('t')
        toolButton.picker = True
        toolButton.realX = self.x + toolButton.x    # toolbar shit
        toolButton.realY = self.y + toolButton.y
        toolButton.show()
        toolMenu.set_x(toolButton.realX - 1)    # line up the menu above the button
        toolMenu.set_y(toolButton.realY)
        self.toolButton = toolButton

        # This thing is already in the menu. Maybe we should reclaim
        # the real estate from the status bar.
        if self.caller.appState.showCharSetButton:
            charSetButton = Button("CharSet", 1, 26, caller.showCharSetPicker, self.window, appState=self.appState)
            # make proper label for character set button
            charSetLabel = self.caller.appState.characterSet
            charSetButton.set_tooltip_command('S')
            if charSetLabel == "Unicode Block":
                charSetLabel = self.caller.appState.unicodeBlock
            charSetLabel = f"{charSetLabel[:3]}.."
            charSetButton.set_label(charSetLabel)
            if self.caller.appState.colorMode == "16":
                charSetButton.hide()
            self.charSetButton = charSetButton
            charSetButton.hide()

        # Brush picker - make me a real brush someday.
        drawCharPicker_offset = toolButton_offset + 6   # to the right of Draw menu
        drawCharPicker_offset += 4  # accomodate for eyedrop for now. yes, this is dumb
        
        drawCharPicker = DrawCharPicker(self.window, caller=self)
        drawCharPickerButton = Button(self.caller.appState.drawChar, 0,  drawCharPicker_offset, drawCharPicker.pickChar, self.window, appState=self.appState)
        drawCharPickerButton.picker = True
        drawCharPickerButton.identity = "drawChar"
        drawCharPickerButton.realX = self.x + drawCharPickerButton.x    # toolbar shit
        drawCharPickerButton.realY = self.y + drawCharPickerButton.y
        drawCharPickerButton.show() 
        #drawCharPickerButton.hide() 
        self.drawCharPickerButton = drawCharPickerButton
        self.drawCharPicker = drawCharPicker

        # This is to make the char picker button hide/show when
        # toolButton's label is set to "Draw"
        self.toolButton.add_sub_button("Draw", drawCharPickerButton)


        #colorPicker = ColorPicker(self.window, x=self.x - 2, y = self.y + 2, caller=caller)
        colorPicker = ColorPicker(self.window, x=self.x - 7, y = self.y + 2, caller=caller)
        self.colorPicker_256 = colorPicker
        self.colorPicker = self.colorPicker_256

        #self.colorPickerButton = Button("FG:  ", 1, 0, colorPicker.showHide, self.window, appState=self.appState)
        self.colorPickerButton = Button("FG:  ", 1, 0, colorPicker.switchTo, self.window, appState=self.appState)
        self.colorPickerButton.invisible = True
        self.colorPickerButton.persistant_tooltip = True
        self.colorPickerButton.set_tooltip_command('c')
        self.colorPickerButton.realX = self.x + self.colorPickerButton.x
        self.colorPickerButton.realY = self.y + self.colorPickerButton.y
        self.items.append(self.colorPickerButton)
        self.buttons.append(self.colorPickerButton)
        self.colorPickerButton.show()
        #if self.caller.appState.colorMode == "256":
        #    self.colorPickerButton.show()
        #else:
        #    self.colorPickerButton.hide()

        colorPicker_16 = ColorPicker(self.window, x=self.x - 7, y = self.y + 2, caller=caller, colorMode="16")
        self.colorPicker_16 = colorPicker_16

        #colorPicker_bg_16 = ColorPicker(self.window, x=self.x - 7, y = self.y + 2, caller=caller, colorMode="16", type="bg")
        #self.colorPicker_bg_16 = colorPicker_bg_16

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
        self.items.append(animButton)
        if self.appState.colorMode != '16': # in 16 color mode, don't cover up the bg color picker
            if self.caller.appState.showCharSetButton:
                self.items.append(charSetButton)
        #self.items.append(fgBgColors)
        #self.items.append(self.swatch)
        self.buttons.append(menuButton)
        self.buttons.append(toolButton)
        self.buttons.append(drawCharPickerButton)
        self.buttons.append(animButton)
        if self.caller.appState.showCharSetButton:
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
        exclude_list = ["drawChar"] # button identities to exclude
        for item in self.items:
            if item.identity not in exclude_list:
                item.show()
        for item in self.buttons:
            if item.identity not in exclude_list:
                item.show()

    def showToolTips(self):
        for item in self.buttons:
            item.handler.showToolTip()
        self.other_tooltips.show()

    def hideToolTips(self):
        for item in self.buttons:
            item.handler.hideToolTip()

    def enableColorPicker(self):
        pass

    def disableColorPicker(self):
        pass

    def setCursorModeMove(self):
        self.caller.appState.setCursorModeMove()
        self.caller.disableMouseReporting()
        self.toolButton.set_label(self.caller.appState.cursorMode)
        #self.drawCharPickerButton.hide()

    def setCursorModeSelect(self):
        self.caller.appState.setCursorModeSelect()
        self.caller.disableMouseReporting()
        self.toolButton.set_label(self.caller.appState.cursorMode)
        #self.drawCharPickerButton.hide()

    def setCursorModeDraw(self):
        self.caller.appState.setCursorModeDraw()
        self.caller.enableMouseReporting()
        self.toolButton.set_label(self.caller.appState.cursorMode)
        #self.drawCharPickerButton.show()

    def setCursorModePaint(self):
        self.caller.appState.setCursorModePaint()
        self.caller.enableMouseReporting()
        self.toolButton.set_label(self.caller.appState.cursorMode)

    def setCursorModeCol(self):
        self.caller.appState.setCursorModeCol()
        self.caller.disableMouseReporting()
        self.toolButton.set_label(self.caller.appState.cursorMode)
        #self.drawCharPickerButton.hide()

    def setCursorModeErase(self):
        self.caller.appState.setCursorModeErase()
        self.caller.disableMouseReporting()
        self.toolButton.set_label(self.caller.appState.cursorMode)
        #self.drawCharPickerButton.hide()

    def setCursorModeEyedrop(self):
        self.caller.appState.setCursorModeEyedrop()
        self.caller.disableMouseReporting()
        #self.toolButton.set_label(self.caller.appState.cursorMode)
        self.toolButton.set_label("Eye")
        #self.drawCharPickerButton.hide()

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




