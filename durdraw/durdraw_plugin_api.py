# Public API for Durdraw plugins.
# Gets instanced and passed into plugin hooks

import curses

import durdraw.durdraw_movie as durdraw_movie
import durdraw.durdraw_options as durdraw_options

class DurPluginAPI:
    """The API object passed to plugins as 'dur'"""
    
    def __init__(self, real_appState):
        # Store the actual app state internally
        self._appState = real_appState 
        self._ui = self._appState.ui
        #self.opts = real_appState.opts 
        self.api_version = 2   # API verison
        self.curses_running = True

    def color_mode(self):
        # The plugin calls this, keeping your internal structure hidden
        return self._appState.colorMode
        
    def suspend_ui(self):
        """ Suspend durdraw UI (ncurses) and reset the terminal, so the plugin can use the terminal however they like """
        curses.def_prog_mode()
        curses.endwin()
        self.curses_running = False

    def resume_ui(self):
        """ Resume ncurses so the plugin can use durdraw UI tools, like notify() """
        curses.reset_prog_mode()
        self.curses_running = True

    # Durdraw-provided UI interactions with the user (requires ncurese
    # not be suspended)
    def notify(self, message, pause=False, wait_time=2500):
        """ Send a message to the user.  By default message shows only for wait_time msec. """
        self._ui.notify(message, pause=pause, wait_time=wait_time)

    def color_picker(self, message=None):
        """ Let the user pick a color using Durdraw's color selector, returns color number """
        # Save old (UI) color setting, so we can use the color picker and then set the color back when done
        ui_fg = self._ui.colorfg
        ui_bg = self._ui.colorbg
        # picker_color is False if user hits Esc in color picker.
        #self.selectColorPicker(message=printMessage)
        picker_color = self._ui.selectColorPicker(message=message)
        self._ui.setFgColor(ui_fg)
        self._ui.setBgColor(ui_bg)
        self._ui.stdscr.refresh()
        return picker_color

    def playback_range(self):
        """ Returns the playback range set in UI """
        return self._appState.playbackRange

    def Frame(self, lines=25, columns=80):
        """ Return a new Frame object """
        return durdraw_movie.Frame(columns, lines)

    def Movie(self, lines=25, columns=80):
        """ Return a new Frame object """
        opts = durdraw_options.Options(width=80, height=25)
        return durdraw_movie.Movie(opts)
