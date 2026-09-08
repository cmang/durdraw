## Durdraw File Format version 8 - August 2026

Durdraw is an ANSI art editor that handles animation, Unicode and 256 color. This document describes its primary file format, "dur."

Durdraw files store color text art (both animated and static) in a file format with the ".dur" file extension. This is a JSON file that has been gzipped. It contains an object named "DurMovie" with a set of key/values specifying metadata and "movie" data. Movie data includes the color format (16 and 256 for now), character encoding, canvas size, frame rate, etc. Metadata includes the artwork name and artist name, which can be used to generate "sauce" records.

"DurMovie" contains an array called "frames." Each element of "frames" is a Frame object, which contains a frame number, a delay amount (in seconds), a "contents" array, and a "colorMap" array.

The "contents" array contains strings, each one of which represents a line of ASCII or Utf-8 text in a frame of art. This can be thought of as a flat ASCII (or Unicode) art file which has been separated into lines, with each line stored as a string in the array.

Similarly, colorMap contains an array of lines, wich each line containing a list of foreground and background color pairs. For example, the pair [1,0] represents blue text with a black background.

Each element of the colorMap should coordinate with a corresponding line and column in the contents. For example, colorMap[2][3] should describe the foreground and background color for the character at contents[2][3], which is the character at Line 2, Column 3 of the given frame.

Here is the full list of JSON keys stored in a DurMovie object, and their purpose:

```
"formatVersion" - The DurDraw file format version
"colorFormat" - The color format of the movie. 16, 256, RGB, mIRC, etc.
"preferredFont" - The preferred font to use (optional)
"encoding" - Text encoding format. Options include "utf-8" and "cp437"
"name" - The name of the movie or artwork
"artist" - The artist name
"framerate" - The playback speed, specified as Frames Per Second
"columns" - The number of columns in the canvas (formerly sizeX)
"lines" - The number of lines in the canvas (formerly sizeY)
"extra" - This can be used to store any JSON object that the user wants to include with their art, perhaps to be used in a custom way. It is not used for anything by Durdraw. (optional)

"frames" - An array of frame objects
"delay" - the amount of time to stay on a frame, in seconds
"contents" - An array of lines containing the ASCII or Unicode artwork
"colorMap" - An array of arrays containing the foreground and background colors for a given line and column in the canvas
```

In 256 color mode, the first 16 colors are as follows:

```
0 black
1 blue
2 green
3 cyan
4 red
5 purple
6 yellow/brown
7 white
8 grey/bright black
9 bright blue
10 bright green
11 bright cyan
12 bright red
13 bright purple
14 bright yellow
15 bright white
```

Colors 16-255 use the standard Xterm-256color palette index.

In 16 color mode, the first 16 colors begin at index 1 instead of 0:

```
1 black
2 blue
3 green
4 cyan
5 red
6 purple
7 yellow/brown
8 white
9 grey/bright black
10 bright blue
11 bright green
12 bright cyan
13 bright red
14 bright purple
15 bright yellow
16 bright white
```

Here is an example Durdraw file, containing an animation with 3 lines, 10 columns and 6 frames:

```
{
  "DurMovie": {
    "formatVersion": 8,
    "colorFormat": "256",
    "preferredFont": "fixed",
    "encoding": "utf-8",
    "name": "",
    "artist": "",
    "framerate": 6.0,
    "columns": 10,
    "lines": 3,
    "extra": null,
    "frames": [
      {
        "frameNumber": 1,
        "delay": 0,
        "contents": [
          "O         ",
          "          ",
          "          "
        ],
        "colorMap": [
          [[12, 0],[1, 0],[7, 0],[7, 0],[7, 0],[7, 0],[7, 0],[7, 0],[7, 0],[1, 0]],
          [[1, 0],[7, 0],[7, 0],[7, 0],[7, 0],[7, 0],[7, 0],[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[1, 0],[1, 0],[7, 0],[7, 0],[7, 0],[1, 0],[1, 0],[1, 0]
          ]
        ]
      },
      {
        "frameNumber": 2,
        "delay": 0,
        "contents": [
          "          ",
          " O        ",
          "          "
        ],
        "colorMap": [
          [[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0]],
          [[1, 0],[12, 0],[7, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0]
          ]
        ]
      },
      {
        "frameNumber": 3,
        "delay": 0,
        "contents": [
          "          ",
          "          ",
          "  O       "
        ],
        "colorMap": [
          [[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0]],
          [[1, 0],[7, 0],[7, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[12, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0]
          ]
        ]
      },
      {
        "frameNumber": 4,
        "delay": 0,
        "contents": [
          "          ",
          "          ",
          "  o       "
        ],
        "colorMap": [
          [[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0]],
          [[1, 0],[7, 0],[7, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[12, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0]
          ]
        ]
      },
      {
        "frameNumber": 5,
        "delay": 0,
        "contents": [
          "          ",
          "   O      ",
          "          "
        ],
        "colorMap": [
          [[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0]],
          [[1, 0],[7, 0],[7, 0],[12, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[7, 0],[12, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0]
          ]
        ]
      },
      {
        "frameNumber": 6,
        "delay": 0,
        "contents": [
          "     O    ",
          "          ",
          "          "
        ],
        "colorMap": [
          [[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[12, 0],[1, 0],[1, 0],[1, 0],[1, 0]],
          [[1, 0],[7, 0],[7, 0],[1, 0],[12, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[7, 0],[7, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0],[1, 0]
          ]
        ]
      }
    ]
  }
}
```

## Changes from Version 7

Version 7 is exactly the same, except for the following changes:

* The key 'lines' is called 'sizeY'

* The key 'columns' is called 'sizeX'

* The 'colorMap' lines/columns index are in reverse orientation from 'contents,' so contents[line][column] maps to the color at colorMap[column][line].

Here is the same example file in version 7 format:

```
{
  "DurMovie": {
    "formatVersion": 7,
    "colorFormat": "256",
    "preferredFont": "fixed",
    "encoding": "utf-8",
    "name": "",
    "artist": "",
    "framerate": 6.0,
    "sizeX": 10,
    "sizeY": 3,
    "extra": null,
    "frames": [
      {
        "frameNumber": 1,
        "delay": 0,
        "contents": [
          "O         ",
          "          ",
          "          "
        ],
        "colorMap": [
          [[12, 8],[1, 0],[1, 0]],
          [[1, 0],[7, 8],[1, 0]],
          [[7, 8],[7, 8],[1, 0]],
          [[7, 8],[7, 8],[1, 0]],
          [[7, 8],[7, 8],[7, 8]],
          [[7, 8],[7, 8],[7, 8]],
          [[7, 8],[7, 8],[7, 8]],
          [[7, 8],[1, 0],[1, 0]],
          [[7, 8],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[1, 0]
          ]
        ]
      },
      {
        "frameNumber": 2,
        "delay": 0,
        "contents": [
          "          ",
          " O        ",
          "          "
        ],
        "colorMap": [
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[12, 8],[1, 0]],
          [[1, 0],[7, 8],[1, 0]],
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[1, 0]
          ]
        ]
      },
      {
        "frameNumber": 3,
        "delay": 0,
        "contents": [
          "          ",
          "          ",
          "  O       "
        ],
        "colorMap": [
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[7, 8],[1, 0]],
          [[1, 0],[7, 8],[12, 8]],
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[1, 0]
          ]
        ]
      },
      {
        "frameNumber": 4,
        "delay": 0,
        "contents": [
          "          ",
          "          ",
          "  o       "
        ],
        "colorMap": [
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[7, 8],[1, 0]],
          [[1, 0],[7, 8],[12, 8]],
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[1, 0]
          ]
        ]
      },
      {
        "frameNumber": 5,
        "delay": 0,
        "contents": [
          "          ",
          "   O      ",
          "          "
        ],
        "colorMap": [
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[7, 8],[1, 0]],
          [[1, 0],[7, 8],[7, 8]],
          [[1, 0],[12, 8],[12, 8]],
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[1, 0]
          ]
        ]
      },
      {
        "frameNumber": 6,
        "delay": 0,
        "contents": [
          "     O    ",
          "          ",
          "          "
        ],
        "colorMap": [
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[7, 8],[1, 0]],
          [[1, 0],[7, 8],[7, 8]],
          [[1, 0],[1, 0],[7, 8]],
          [[1, 0],[12, 8],[1, 0]],
          [[12, 8],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[1, 0]],
          [[1, 0],[1, 0],[1, 0]
          ]
        ]
      }
    ]
  }
}
```


History:

Version 8 - Durdraw 0.30.0 - August 2026 - Fixed colorMap x/y vs y/x issue, and lines/columns vs sizeY/sizeX

Version 7 - May 2023 - First public JSON/GZIP version

