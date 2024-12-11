# Undo Register

- [Undo Register](#undo-register)
  - [Undo usages](#undo-usages)
    - [Summarised](#summarised)


## Undo usages

| undo method | file | Line | Function |
| --- | --- | --- | --- |
`push()` | durdraw/durdraw_ui_curses.py | 1097 | `def transform_bounce(self):` |
`push()` | durdraw/durdraw_ui_curses.py | 1107 | `def transform_repeat(self):` |
`push()` | durdraw/durdraw_ui_curses.py | 1117 | `def transform_reverse(self):` |
`push()` | durdraw/durdraw_ui_curses.py | 1126 | `def moveCurrentFrame(self):` |
`push()` | durdraw/durdraw_ui_curses.py | 1386 | `def apply_neofetch_keys(self):` |
`push()` | durdraw/durdraw_ui_curses.py | 2614 | `def mainLoop(self):` |
`push()` | durdraw/durdraw_ui_curses.py | 3372 | `def replaceColorUnderCursor(self):` |
`push()` | durdraw/durdraw_ui_curses.py | 3427 | `def cloneToNewFrame(self):` |
`push()` | durdraw/durdraw_ui_curses.py | 3437 | `def appendEmptyFrame(self):` |
`push()` | durdraw/durdraw_ui_curses.py | 3611 | `def getDelayValue(self):` |
`push()` | durdraw/durdraw_ui_curses.py | 3630 | `def deleteCurrentFramePrompt(self):` |
`push()` | durdraw/durdraw_ui_curses.py | 5314 | `def loadFromFile(self, shortfile, loadFormat):  # shortfile = non full path filename` |
`push()` | durdraw/durdraw_ui_curses.py | 6446 | `def addColToCanvas(self):` |
`push()` | durdraw/durdraw_ui_curses.py | 6459 | `def delColFromCanvas(self):` |
`push()` | durdraw/durdraw_ui_curses.py | 6475 | `def addLineToCanvas(self):` |
`push()` | durdraw/durdraw_ui_curses.py | 6487 | `def delLineFromCanvas(self):` |
`push()` | durdraw/durdraw_ui_curses.py | 6501 | `def addCol(self, frange=None):` |
`push()` | durdraw/durdraw_ui_curses.py | 6524 | `def delCol(self, frange=None):` |
`push()` | durdraw/durdraw_ui_curses.py | 6543 | `def delLine(self, frange=None):` |
`push()` | durdraw/durdraw_ui_curses.py | 6564 | `def addLine(self, frange=None):` |
`push()` | durdraw/durdraw_ui_curses.py | 6582 | `def startSelecting(self, firstkey=None, mouse=False):   # firstkey is the key the user was` |
`push()` | durdraw/durdraw_ui_curses.py | 6853 | `def askHowToPaste(self):` |
`push()` | durdraw/durdraw_ui_curses.py | 6876 | `def pasteFromClipboard(self, startPoint=None, clipBuffer=None, frange=None, transparent=False, pushUndo=True):` |
`push()` | durdraw/durdraw_ui_curses.py | 6927 | `def copySegmentToAllFrames(self, startPoint, height, width, frange=None):` |
`push()` | durdraw/durdraw_ui_curses.py | 6972 | `def flipSegmentVertical(self, startPoint, height, width, frange=None):` |
`push()` | durdraw/durdraw_ui_curses.py | 6984 | `def flipSegmentHorizontal(self, startPoint, height, width, frange=None):` |
`push()` | durdraw/durdraw_ui_curses.py | 6995 | `def deleteSegment(self, startPoint, height, width, frange=None):` |
`push()` | durdraw/durdraw_ui_curses.py | 7011 | `def fillSegment(self, startPoint, height, width, frange=None, fillChar=\"X\"):` |
`push()` | durdraw/durdraw_ui_curses.py | 7027 | `def colorSegment(self, startPoint, height, width, frange=None):` |
`push()` | durdraw/durdraw_ui_curses.py | 764 | `def backspace(self):` |
`push()` | durdraw/durdraw_ui_curses.py | 774 | `def deleteKeyPop(self, frange=None):` |
`push()` | durdraw/durdraw_ui_curses.py | 790 | `def reverseDelete(self, frange=None):` |
`push()` | durdraw/durdraw_ui_curses.py | 807 | `def insertColor(self, fg=1, bg=0, frange=None, x=None, y=None, pushUndo=True):` |
`push()` | durdraw/durdraw_ui_curses.py | 823 | `def insertChar(self, c, fg=1, bg=0, frange=None, x=None, y=None, moveCursor = False, pushUndo=True):` |
`push()` | durdraw/durdraw_ui_curses.py | 878 | `def clearCanvas(self, prompting = False):` |
`push()` | durdraw/durdraw_undo.py | 10 | `def __init__(self, ui, appState = None):` |
`push()` | durdraw/durdraw_undo.py | 42 | `def undo(self):` |
`undo()` | durdraw/durdraw_ui_curses.py | 1126 | `def moveCurrentFrame(self):` |
`undo()` | durdraw/durdraw_ui_curses.py | 2584 | `def clickedUndo(self):` |
`undo()` | durdraw/durdraw_ui_curses.py | 6582 | `def startSelecting(self, firstkey=None, mouse=False):   # firstkey is the key the user was` |
`redo()` | durdraw/durdraw_ui_curses.py | 2592 | `def clickedRedo(self):` |

### Summarised

✅ == involves pixel changes
❓ == unsure

- columns ✅
  - deleting/adding columns ✅
- chars/colours ✅
  - inserting chars/colours ✅
  - replacing colours ✅
- backspace
- segment ❓
  - flipping/deleting/filling/colouring ✅
- clear canvas ✅
- frame ✅
  - moving/cloning/appending/deleting ✅
- lines ✅
  - deleting/adding lines ✅
- transform ❓
  - bounce/repeat/reverse ❓


## Feature List

1. pixel-level undo/redo
    - Allow undo/redo to be applied against individual pixels rather than cycling through the undo stack across all frames
2. frame-level undo/redo
    - Allow undo/redo to be applied against a specific frame rather than cycling through the undo stack across all frames
3. movie-level undo/redo
    - Allow undo/redo at a global/movie level
4. (?) action/state-level undo/redo
    - Allow undo/redo for actions that are not pixel/char/colour changes
    - e.g. cursor position, selected area, durations/other metadata


- Any changes to pixel/frame undo register should reflect in the movie-level undo register.

## Implementation

There are many scattered usages of the undo state machine. There are many actions that affect the state of pixels,
frames and the movie, and each of these callers are the ones that also directly adjust the undo state.

This makes changes difficult as there are many use cases to contend with that seem different on the surface, but in
reality are mostly modifying chars/colours

Each existing action should be routed (where appropriate) through the Frame/Movie classes. These classes are best placed
to recognise when state has changed and correspondingly update the undo state. In addition to the existing Frame/Movie classes, it would be
 handy to introduce something like a Pixel class that could keep track of its ownstate too. I'm unsure how this would interact with things like the existing colour map #TODO investigate.

This move would allow easier implementation of pixel/frame/movie-level undo/redos.

Ideally, functionally:

- Any changes to pixel/frame undo register should reflect in the movie-level undo register.
- State other than pixel char/colour changes should be considered for undo/redo
  - cursor position
  - selected area
  - durations/other metadata
- All state should be updated correctly from undo/redo actions, at any and all levels (pixel/frame/movie/action)
- All state changes of a certain level should propagate correctly and immediately to all other levels
- The user should be able to switch between any undo/redo level at any time, and apply any direction of undo/redo
- Goes without saying
  - This should all be _fast_, which I'm pretty confident will be the case (#TODO some basic proof and big Os).
  - This should be _efficient_, leaving room for very large projects and scaling/extending in future.
  - This should all be _small_, as any speed increase at the cost of memory will not really be a victory.

## Considerations & Challenges

- For operations like "flipping", this will require storing many pixel changes
  - will need to ensure that nothing is missed, and that the operation is not slow
