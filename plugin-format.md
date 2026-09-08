Durdraw Plugin Format Specification, Durdraw Extension API: draft 0.2

THIS IS A BETA API.  It is subject to change.

Durdraw 0.30.0 and higher allows users to add their own features and extensions through a Plugins API.

Users can create these plug-in types:

* Effects
* Export
* Menu Items

Durdraw plugins are Python scripts with the .py file extension.  They can be placed in ~/.durdraw/plugins/ and will be loaded when Durdraw starts.

The script contains some metadata to register itself. For example:

```python
# Durdraw plugin format version
durdraw_plugin_version = 2

# Plugin information
durdraw_plugin = {
    "name": "Random Colors",
    "author": "Author name, email@address.com",
    "version":  1,   # Version of the specific plugin
    "provides": ["transform_movie"],
    "type": ["effect"],
    "desc": "Fill canvas with random Colors."
}
```

To provide optional parameters, include the "opts" {} dict. Durdraw will prompt the user to specify these options, or will use the defaults you provide. These options are then passed back into the plugin. For example:

```python
opts = {
    'min color': 1,
    'max color': 255,
}
```

Most plug-ins work by providing a function called transform_movie(), which returns a Movie object that becomes the new canvas, like so:

```python
def transform_movie(dur, opts, mov):
    ...
    return mov
```

transform_movie() is passed 3 objects:
    * dur - an object containing general Durdraw API methods
    * opts - The user-provided options to the plugin
    * mov - The canvas/movie object (a collection of frames)

These methods are provided by Durdraw, and can be used in plugins:

| Method | Description |
| :--- | :--- |
| `dur.color_mode()` | The current color mode, "16" or "256" |
| `dur.suspend_ui()` |  Suspend Durdraw UI (curses), so another TUI can be loaded |
| `dur.resume_ui()` | Resume Durdraw UI (curses), so the plugin can return to Durdraw |
| `dur.notify(message, pause=True)` | Send a notification message to the user. pause optionally keeps the message up on the screen until the user presses a key. |
| `dur.color_picker(message=None)` | Opens the color picker for the user, returns an integer containing the selected color value. Optionally message contains a message to show the user while the color picker is open. |
| `dur.playback_range()` | Returns a tuple containing the playback range set in the UI. |
| `dur.Movie(lines=25, columns=80)` | returns a new empty Movie object. |

"mov" is the currently loaded Movie, passed into the plugin from Durdraw. A Movie is a collection of frames (in mov.frames[]) making up the canvas contents, and contains these helper methods:

| Method | Description |
| :--- | :--- |
| `mov.width()` | Returns width (number of columns) of movie/canvas |
| `mov.height()` | Return height (number lines) of movie/canvas |
| `mov.addFrame(frame)` | Takes a Frame object and appends it to the end of the movie |
| `mov.insertFrame(frame)` | Takes a frame object and inserts it after the "current" frame (the frame in the user's canvas) |
| `mov.addEmptyFrame()` | Appends an empty frame to the movie
| `mov.insertCloneFrame()` | Clones current frame and adds it after the current frame |
| `mov.deleteCurrentFrame()` | Deletes the current frame |
| `mov.moveFramePosition(startPosition, newPosition)` | Moves the frame at startPosition to newPosition |
| `mov.gotoFrame(frameNumber)` | frameNumber becomes the current frame |
| `mov.nextFrame()` | Go to the next frame (next frame becomes current frame), or wrap around to the first frame if current frame is the last frame in the movie |
| `mov.prevFrame()` | Go to the previous frame (previous frame becomes current frame), or wrap around to the last frame if current frame is the first frame |
| `mov.growCanvasWidth(growthSize)` | Add growthSize number of columns to the canvas (affects all frames) |
| `mov.shrinkCanvasWidth(shrinkSize)` | Shrinks the canvas by removing rightmost shrinkSize number of columns |
| `mov.hasMultipleFrames()` | Returns True if the movie has multiple frames, or False if there is only one frame |
| `frame.width()` | Returns width (number of columns) of the frame |
| `frame.height()` | Return height (number lines) of the frame |
| `frame.setDelayValue()` | takes a float, and sets the timing delay for the specified frame. |

The following properties are available:

| Property | Description |
| :--- | :--- |
| `mov.frames[]` | A list of Frame objects, which make up the currently loaded movie. |
| `frame.content` | The unicode characters in the frame (without color data) |
| `frame.content[line][col]` | read or write to the character at index line and column |
| `frame.colorMap` | The color data in the frame (without character data) |
| `frame.colorMap[line][col]` | read or write to the color at index line and column |

Here is an example Effects that places random letters and colors on all frames of the movie:

```python
# Durdraw Plugin

import random
import string

# Durdraw plugin format version
durdraw_plugin_version = 2

# Plugin information
durdraw_plugin = {
    "name": "random letters and colors",
    "author": "Sam Foster, samfoster@gmail.com",
    "version":  1,   # Plugin version, if applicable
    "provides": ["transform_movie"],
    "type": ["effect"],
    "desc": "Fill canvas with random letters and colors."
}

opts = {
    'min color': 1,
    'max color': 255
}

def transform_movie(dur, opts, mov):
    frame_num = 0
    for frame in mov.frames:
        mov.frames[frame_num] = randomizer(dur, opts, frame)
        frame_num += 1
    return mov

def randomizer(dur, opts, frame):
    # fill canvas with random letters.
    for line_num in range(frame.height()):
        for col_num in range(frame.width()):
            frame.content[line_num][col_num] = random.choice(string.ascii_letters)

    # Fill canvas with random colors.
    if dur.color_mode() == "256":
        min_color = opts['min color']
        max_color = opts['max color']
        bg_color = 0
    else:
        min_color = 1
        max_color = 15
        bg_color = 0

    for line_num in range(frame.height()):
        for col_num in range(frame.width()):
            # Fg colr
            frame.colorMap[line_num][col_num][0] = random.randrange(min_color, max_color + 1)
            # Bg colr
            frame.colorMap[line_num][col_num][1] = 0
    return frame
```

Here is an example Menu Item plugin:

```python
import curses, os, subprocess

# Durdraw plugin format version
durdraw_plugin_version = 2

# Plugin information
durdraw_plugin = {
    "name": "Jump to Shell",    # Item as it apperas in the menu
    "author": "",
    "version": 1,
    "provides": ["transform_movie"],
    "desc": "Jump out to the shell, similar to Jump to DOS in TheDraw",
    # Menu stuff
    "type": "menu_item",
    "shortcut": "j",       # Keyboard shurtcut when menu is open
    "location": "Menu"     # Menu for submenu to go in
}

# Plugin options
opts = {
}

def transform_movie(dur, opts, mov):
    dur.suspend_ui()
    shell = os.getenv("SHELL")
    print("Type 'exit' to return to durdraw.")
    subprocess.run(shell)
    input('Press enter to return to Durdraw...')
    dur.resume_ui()
    return mov
```
