# Takes clicks from gui_manager's Gui() objects and.. does stuff?

class GuiHandler():
    def __init__(self, gui):
        self.gui = gui
        self.window = gui.window
        self.debugLine = 30 

    def got_click(self, clickType, y, x, extra=None):
        #self.window.addstr(self.debugLine, 0, f"Clicked: {x}, {y}, {clickType}.")
        # if a button was clicked, tell it:
        z = 0 
        for button in self.gui.buttons:
            #self.window.addstr(32 + z, 0, f"{button.label}, {button.realX}, {button.realY}")
            z += 1
            if x == button.realX:   # if it's on the line and within width area
                if (y >= button.realY) and (y <= button.realY + button.width):
                    #self.window.addstr(33 + z, 0, f"Clicky")
                    button.on_click()

