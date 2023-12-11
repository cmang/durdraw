# Takes clicks from gui_manager's Gui() objects and.. does stuff?

import pdb

class GuiHandler():
    def __init__(self, gui):
        self.gui = gui
        self.window = gui.window
        self.debugLine = 30 

    def got_click(self, clickType, y, x, extra=None):
        #self.window.addstr(self.debugLine, 0, f"Clicked: {x}, {y}, {clickType}.")
        # if a button was clicked, tell it:
        for button in self.gui.buttons:
            if x == button.realX:   # if it's on the line and \/ within width area
                if (y >= button.realY) and (y <= button.realY + button.width + 1):
                    #self.window.addstr(33 + z, 0, f"Clicky")
                    #pdb.set_trace()
                    button.on_click()

