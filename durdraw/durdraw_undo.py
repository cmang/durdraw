import pickle
import tempfile

class UndoManager():  # pass it a UserInterface object so Undo can tell UI
        # when to switch to another saved movie state.
        """ Manages undo/redo "stack" by storing the last 100 movie states
            in a list. Takes a UserInterface object for syntax. methods for
            push, undo and redo """
        def __init__(self, ui, appState = None):
            self.ui = ui
            self.undoIndex = 0 # will be 0 when populated with 1 state.
            self.modifications = 0 #
            self.undoList = []
            self.historySize = 100  # default, but really determined by
            self.appState = appState
            # AppState values passed to setHistorySize() below.
            self.push() # push initial state

        def push(self): # maybe should be called pushState or saveState?
            """ Take current movie, add to the end of a list of movie
                objects - ie, push current state onto the undo stack. """
            if self.modifications > 0:
                if self.appState.modified == False:
                    self.appState.modified = True
            self.modifications += 1
            if len(self.undoList) >= self.historySize:   # How far back our undo history can
                # go. Make this configurable.
                # if undo stack == full, dequeue from the bottom
                self.undoList.pop(0)
            # if undoIndex isn't indexing the last item in undoList,
            # ie we have redo states, remove all items after undoList[undoIndex]
            self.undoList = self.undoList[0:self.undoIndex]  # trim list
            # then add the new state to the end of the queue.

            # create a temporary file to store the pickled movie object
            f = tempfile.TemporaryFile()
            pickle.dump(self.ui.mov, f)
            f.seek(0)
            self.undoList.append(f)

            # last item added == at the end of the list, so..
            self.undoIndex = len(self.undoList) # point index to last item

        def undo(self):
            if self.modifications > 1:
                self.modifications = self.modifications - 1
            if self.modifications == 2:
                self.appState.modified = False
            if self.undoIndex == 1: # nothing to undo
                self.ui.notify("Nothing to undo.")
                return False
            # if we're at the end of the list, push current state so we can
            # get back to it. A bit confusing.
            if self.undoIndex == len(self.undoList):
                self.push()
                self.undoIndex -= 1
            self.undoIndex -= 1
            self.ui.mov = pickle.load(self.undoList[self.undoIndex]) # set UI movie state
            self.undoList[self.undoIndex].seek(0)
            return True # succeeded

        def redo(self):
            if self.undoIndex < (len(self.undoList) -1): # we can redo
                self.undoIndex += 1 # go to next redo state
                self.modifications += 1

                self.ui.mov = pickle.load(self.undoList[self.undoIndex]) # set UI movie state
                self.undoList[self.undoIndex].seek(0)

                if self.appState.modified == False:
                    self.appState.modified = True
            else:
                self.ui.notify("Nothing to redo.")
        def setHistorySize(self, historySize):
            """ Defines the max number of undo states we will save """
            self.historySize = historySize


