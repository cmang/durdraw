# Handlers for durdraw_ui_widgets.py classes

import curses
import pdb
import time
import curses.panel

def curses_cursorOff():
    try:
        curses.curs_set(0)  # turn off cursor
    except curses.error:
        pass    # .. if terminal supports it.

def curses_cursorOn():
    try:
        curses.curs_set(1)  # turn on cursor
    except curses.error:
        pass    # .. if terminal supports it.

def curses_notify(screen, message, pause=False):
    #screen.cursorOff()
    #screen.clearStatusLine()
    screen.addstr(0, 0, message)
    screen.refresh()
    if pause:
        if screen.playing:
            screen.nodelay(0) # wait for input when calling getch
            screen.getch()
            screen.nodelay(1) # do not wait for input when calling getch
        else:
            screen.getch()
    if not pause:
        curses.napms(1500)
        curses.flushinp()
    #screen.clearStatusLine()
    #screen.cursorOn()
    screen.refresh()

def curses_addstr(window, y, x, text, attr=None): # addstr(y, x, str[, attr]) and addstr(str[, attr])
    """ Wraps curses addstr in a try;except, prevents addstr from
        crashing cureses if it fails """
    if not attr:
        try:
            window.addstr(y, x, text)
        except curses.error as e:
            curses_notify(window, f"Debug: Curses error in addstr(): {e.args[0]}")
            #self.testWindowSize()
    else:
        try:
            window.addstr(y, x, text, attr)
        except curses.error:
            pass    # silent ugly fail
            #curses_notify(window, f"Debug: Curses error in addstr(): {curses.error}")
            #self.testWindowSize()

class MenuHandler:
    """ hook into Curses to draw menu 
    """
    def __init__(self, menu, window):
        self.menu = menu
        self.window = window
        self.parentWindow = self.menu.caller.window
        self.x = menu.x
        self.y = menu.y
        self.menuOriginLine = 0
        #self.rebuild()
        #self.panel = curses.panel.new_panel(self.curses_win)

    def rebuild(self):
        height = len(self.menu.items) 
        # find widest item in list, go a few characters larger 
        width = len(max(self.menu.items, key = len)) + 4
        self.x = self.menu.x - height
        self.curses_win = curses.newwin(height, width, self.x, self.y)
        #self.curses_win.border()
        line = 0
        textColor = curses.color_pair(1) | curses.A_BOLD
        buttonColor = curses.color_pair(6) | curses.A_BOLD
        maxX, maxY = self.parentWindow.getmaxyx()
        self.menuOriginLine = maxX - 2 - height
        for (item, button) in zip(self.menu.items, self.menu.buttons):
            #newButton = Button(button.label, line, 0, button.on_click, self.curses_win)
            #self.menu.buttons.remove(button)
            #self.menu.buttons.add(newButton)
            #curses_addstr(self.curses_win, line, 0, item, textColor)
            curses_addstr(self.curses_win, line, self.menu.y, item, textColor)
            #curses_addstr(self.curses_win, line, 0, item, color)
            top_of_menu = self.menu.caller.y - len(self.menu.buttons)
            #button.update_real_xy(x=self.menu.caller.x, y=top_of_menu + line)
            #button.update_real_xy(x=line, y=0) # working for putting menu on first line
            button.update_real_xy(x=self.menuOriginLine + line, y=self.menu.y) # working for putting menu on first line
            button.window = self.window
            line += 1
        self.panel = curses.panel.new_panel(self.curses_win)
        self.panel.hide()

    def show(self):
        self.rebuild()
        self.panel.top()
        #self.panel.move(0,0)
        #self.panel.move(self.menuOriginLine, 0)
        #self.panel.move(self.menuOriginLine, self.menu.x)
        self.panel.move(self.menuOriginLine, self.menu.y)
        self.panel.show()
        self.curses_win.keypad(True)
        curses.panel.update_panels()
        curses.doupdate()
        self.curses_win.refresh()
        # Input loop
        self.window.nodelay(1)
        #self.curses_win.nodelay(0)
        prompting = True
        options = []
        current_option = 0
        for item in self.menu.items:
            options.append(item)
        self.refresh()
        curses_cursorOff()
        #pdb.set_trace()
        #curses.mousemask(1)
        #print('\033[?1003l') # disable mouse reporting
        while(prompting):
            time.sleep(0.01)
            line = 0
            c = self.window.getch()
            for item in self.menu.items:
                if item == options[current_option]: # selected item
                    textColor = curses.color_pair(1) | curses.A_REVERSE
                else:
                    textColor = curses.color_pair(1) | curses.A_BOLD
                curses_addstr(self.curses_win, line, 0, item, textColor)
                line += 1
                #pdb.set_trace()
                curses.panel.update_panels()
                self.window.refresh()
                if c == ord(self.menu.items[item]["hotkey"]):    # hotkey pressed
                    self.hide()
                    self.menu.items[item]["on_click"]()
                    prompting = False
            if c == curses.KEY_UP:
                current_option = max(0, current_option - 1)
                #pdb.set_trace()
            elif c == curses.KEY_DOWN:
                current_option = min(len(options) - 1, current_option + 1)
            elif c in [13, curses.KEY_ENTER]:    # selected an option
                #pdb.set_trace()
                self.hide()
                prompting = False
                # yikes lol
                self.menu.items[options[current_option]]["on_click"]() 
            elif c == 27:  # normal esc
                self.hide()
                prompting = False
            elif c == curses.KEY_MOUSE:
                try:
                    _, mouseX, mouseY, _, _ = curses.getmouse()
                except:
                    pass
                #pdb.set_trace()
                self.hide()
                prompting = False
                self.menu.gui.got_click("Click", mouseX, mouseY)
                #curses_notify(self.window, f"Click: x={mouseX}, y={mouseY}")
                #a_button = self.menu.buttons[1]
                #curses_notify(self.window, f"second button: {a_button.label}, realX: {a_button.realX}, realY: {a_button.realY}")
            #jif c in [104, 63]:  # h H Help
            #    self.hide()
            #    self.items["Help"]["on_click"]()
            #    prompting = False
        #pdb.set_trace()
        curses_cursorOn()
        self.menu.hide()
        if not self.menu.caller.caller.playing:    # lol .. the caller.caller is the main UI thing
            self.window.nodelay(0)
        #curses_addstr(self.window, self.menu.x, self.menu.y, "Show menu")

    def refresh(self):
        self.window.refresh()
        curses.panel.update_panels()
        #self.window.move(0,0)
        curses.doupdate()

    def hide(self):
        self.panel.hide()
        self.refresh()
        #curses_addstr(self.window, self.menu.x, self.menu.y, "Hide menu")

class DrawCharPickerHandler:
    def __init__(self, caller, window):
        self.caller = caller    # drawCharPicker
        self.window = window

    def pickChar(self):
        maxLines, maxCol = self.window.getmaxyx()
        #pdb.set_trace()
        self.window.addstr(maxLines - 3, 0, "Enter a character to use for drawing: ")
        prompting = True
        while prompting:
            c = self.window.getch()
            time.sleep(0.01)
            if c in [curses.KEY_F1]:
                self.caller.appState.drawChar = chr(self.caller.caller.caller.chMap['f1'])
                prompting = False
            elif c in [curses.KEY_F2]:
                self.caller.appState.drawChar = chr(self.caller.caller.caller.chMap['f2'])
                prompting = False
            elif c in [curses.KEY_F3]:
                self.caller.appState.drawChar = chr(self.caller.caller.caller.chMap['f3'])
                prompting = False
            elif c in [curses.KEY_F4]:
                self.caller.appState.drawChar = chr(self.caller.caller.caller.chMap['f4'])
                prompting = False
            elif c in [curses.KEY_F5]:
                self.caller.appState.drawChar = chr(self.caller.caller.caller.chMap['f5'])
                prompting = False
            elif c in [curses.KEY_F6]:
                self.caller.appState.drawChar = chr(self.caller.caller.caller.chMap['f6'])
                prompting = False
            elif c in [curses.KEY_F7]:
                self.caller.appState.drawChar = chr(self.caller.caller.caller.chMap['f7'])
                prompting = False
            elif c in [curses.KEY_F8]:
                self.caller.appState.drawChar = chr(self.caller.caller.caller.chMap['f8'])
                prompting = False
            elif c in [curses.KEY_F9]:
                self.caller.appState.drawChar = chr(self.caller.caller.caller.chMap['f9'])
                prompting = False
            elif c in [curses.KEY_F10]:
                self.caller.appState.drawChar = chr(self.caller.caller.caller.chMap['f10'])
                prompting = False
            else:
                self.caller.appState.drawChar = chr(c)
                prompting = False
        self.caller.caller.drawCharPickerButton.label = self.caller.appState.drawChar
        self.window.addstr(maxLines - 3, 0, "                                          ")
        self.caller.caller.caller.refresh()

class ColorPickerHandler:
    def __init__(self, colorPicker, window):
        self.colorPicker = colorPicker
        self.parentWindow = window
        self.x = colorPicker.x
        self.y = colorPicker.y
        self.parentWindow = colorPicker.caller.stdscr
        self.appState = colorPicker.caller.appState
        # figure out picker size
        total = curses.COLORS
        realmaxY,realmaxX = self.parentWindow.getmaxyx()
        self.realmaxY = realmaxY
        self.realmaxX = realmaxX
        #self.height = int(total / realmaxX) + 2 # enough lines to fill content+
        self.height = 4
        #height = int(total / realmaxY) # enough lines to fill content+
        #self.width = realmaxX - 10 
        self.width = 78
        #gridLine = [[]] * self.width
        #self.colorGrid = [gridLine] * self.height
        #self.colorGrid = [[0] * self.width] * self.height
        self.colorGrid = [[0 for i in range(self.width)] for j in range(self.height)]
        self.window = curses.newwin(self.height, self.width, self.x, self.y)
        self.window.keypad(True)
        self.curses_win = self.window
        self.panel = curses.panel.new_panel(self.curses_win)
        self.panel.hide()
        #self.fillChar = 9608    # unicode block
        self.fillChar = self.appState.colorPickChar# unicode block
        self.origin = self.x - 2
        #self.move(0,self.x - 2)
        self.move(0,self.origin)

    def show(self):
        self.showFgPicker()

    def hide(self):
        self.panel.bottom()
        self.panel.hide()

    def move(self, x, y):
        self.x = x
        self.y = y
        self.panel.move(y, x)
        #self.origin = self.x - 2

    def updateFgPicker(self):
        line = 0
        col = 0
        #maxWidth = self.realmaxX
        #maxHeight = self.realmaxY
        for fg in range(1,curses.COLORS):  # 0-255
            color_pair = curses.color_pair(fg)
            if col >= self.width - 2:
                col = 0
                line += 1
            self.colorGrid[line][col] = fg
            #if line > 0:
            #    pdb.set_trace()
            #curses_addstr(self.window, self.colorPicker.y + line, self.colorPicker.x + col, chr(self.fillChar), color_pair)
            # if fg == app's current fg, draw it as a * instead of self.fillChar
            if fg == self.colorPicker.caller.colorfg:
                curses_addstr(self.window, line, col, '*', color_pair)
            else:
                curses_addstr(self.window, line, col, chr(self.fillChar), color_pair)
            col += 1

    def showFgPicker(self):
        self.showColorPicker(type="fg")

    def showColorPicker(self, type="fg"):
        """ Shows picker, has UI loop for letting user pick color with keyboard or mouse """
        if type == "fg":
            self.updateFgPicker()
        elif type == "bg":
            self.updateBgPicker()
        prompting = True
        self.window.nodelay(1)
        #print('\033[?1003l') # disable mouse movement tracking (xterm api)
        #curses.mousemask(1)
        curses_cursorOff()
        # populate window with colors
        self.panel.top()
        #self.move(0,self.x - 6)
        self.panel.show()
        prompting = True
        oldColor = self.colorPicker.caller.colorfg
        color = self.colorPicker.caller.colorfg
        while(prompting):
            time.sleep(0.01)
            self.colorPicker.caller.drawStatusBar()
            self.update()
            c = self.window.getch()
            if c in [98, curses.KEY_LEFT]:
                if color == 0:
                    color = curses.COLORS - 1
                else:
                    color -= 1
                #self.colorPicker.caller.colorfg = color
                self.colorPicker.caller.setFgColor(color)
                self.updateFgPicker()
            elif c in [102, curses.KEY_RIGHT]:
                color += 1
                if color >= curses.COLORS:
                    color = 0
                #self.colorPicker.caller.colorfg = color
                self.colorPicker.caller.setFgColor(color)
                self.updateFgPicker()
            elif c == curses.KEY_UP:
                color -= self.width - 2
                if color <= 0:
                    color = 1
                self.colorPicker.caller.setFgColor(color)
                self.updateFgPicker()
            elif c == curses.KEY_DOWN:
                color += self.width - 2
                if color >= curses.COLORS:
                    color = curses.COLORS - 1
                self.colorPicker.caller.setFgColor(color)
                self.updateFgPicker()
            elif c in [13, curses.KEY_ENTER]:   # Return, Accept color
                self.hide()
                prompting = False
                pass
            elif c == curses.KEY_MOUSE:
                try:
                    _, mouseX, mouseY, _, _ = curses.getmouse()
                except:
                    pass
                if mouseY >= self.origin and mouseX < len(self.colorGrid[0])-2:   # cpicked in the color picker
                    clickedCol = mouseX
                    clickedLine = mouseY - self.origin
                    #if clickedCol < len(self.colorGrid[clickedLine])-2:
                    if mouseY < self.origin + self.height:
                        if self.colorGrid[clickedLine][clickedCol] != 0:
                            color = self.colorGrid[clickedLine][clickedCol]
                            self.colorPicker.caller.setFgColor(color)
                    #curses_notify(self.parentWindow, f"clicked col: {clickedCol}, line: {clickedLine}, color: {color}")
                    #pdb.set_trace()
                self.hide()
                prompting = False
            elif c == 27:  # normal esc, Cancel
                c = self.window.getch()
                if c == curses.ERR: # Just esc was hit, no other escape sequence
                    self.colorPicker.caller.setFgColor(oldColor)
                    self.hide()
                    prompting = False
                    color = oldColor
        self.hide()
        curses_cursorOn()
        self.window.nodelay(0)
        #curses.mousemask(curses.REPORT_MOUSE_POSITION | curses.ALL_MOUSE_EVENTS)
        #print('\033[?1003h') # enable mouse tracking
        return color

    def update(self):
        curses.panel.update_panels()
        curses.doupdate()
        self.window.refresh()

class ColorSwatchHandler:
    def __init__(self, colorSwatch, window):
        self.colorSwatch = colorSwatch
        self.window = window
        self.fillChar = 9608    # unicode block
    def draw(self, plusX=0, plusY=0):
        for c in range(0, len(self.colorSwatch.bank)-1):
            curses_addstr(self.window, self.colorSwatch.y, self.colorSwatch.x, chr(self.fillChar))

class FgBgColorPickerHandler:
    def __init__(self, fgBgPicker, x=0, y=0):
        self.fgBgPicker = fgBgPicker
        self.window = fgBgPicker.window 
        self.x = x
        self.y = y
        #self.on_click = on_click
    def draw(self, plusX=0, plusY=0):
        curses_addstr(self.window, self.y, self.x, "F:  G:  ")

class ButtonHandler:
    """ hook into Curses to draw button
    """
    def __init__(self, button, window, on_click):
        #self.label = button.label
        self.button = button
        self.window = window
        self.x = self.button.x
        self.y = self.button.y
        self.on_click = on_click
        self.color = curses.color_pair(6) | curses.A_BOLD   # bright green, clickable

    def draw(self, plusX=0, plusY=9):
        if not self.button.invisible:
            textColor = self.color
            if self.button.selected:
                textColor = textColor | curses.A_REVERSE
            #curses_addstr(self.window, plusX + self.button.x, plusY + self.button.y, self.button.label)
            #curses_addstr(self.window, plusX + self.button.x, plusY + self.button.y, self.button.label, self.color)
            curses_addstr(self.window, self.button.realX, self.button.realY, self.button.label, textColor)
            # render the button on the window

    def on_click(self):
        curses_addstr(self.window, 0, 0, f"{self.button.label} clicked")

    def update_real_xy(x=0, y=0):
        self.button.realX = x
        self.button.realY = y

    def handle_event(self, event):
        # handle events for the button
        if event.type == 'click':
            self.on_click()
        return True

class StatusBarHandler:
    def __init__(self, statusBar, window): 
        self.statusBar = statusBar
        self.window = window
        self.panel = curses.panel.new_panel(self.window)
        #curses_addstr(window, self.statusBar.x, self.statusBar.y, "Fnord")
        #self.on_click = on_click

    def draw(self, plusX=0, plusY=0):
        pass
        #for item in self.statusBar.items:
        #    curses_addstr(self.window, self.statusBar.x + item.x, self.statusBar.y + item.y, item.label)

    def handle_event(self, event):
        # handle events for the button
        if event.type == 'click':
            self.on_click()
        return True



