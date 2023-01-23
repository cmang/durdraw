# Does things like: Takes a mouse click command. eg: left click on X, y.
# Figures out which widget got clicked (if any), tells the widget to run
# its onClick

# Eventually this should also do things like tell the GUI handler (curses
# or kivy) to initialize

from durdraw.durdraw_gui_manager_curses import GuiHandler

class Gui():
    def __init__(self, guiType=None, window=None):
        self.window = window
        self.handler = GuiHandler(self)
        self.widgets = []
        self.buttons = []

    def add_button(self, widget):
        self.buttons.append(widget)

    def del_button(self, widget):
        self.buttons.remove(widget)

    def got_click(self, clickType, x, y, extra=None):
        self.handler.got_click(clickType, x, y, extra=None)
