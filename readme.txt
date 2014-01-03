                  __                __
                _|  |__ __ _____ __|  |_____ _____ __ __ __
               / _  |  |  |   __|  _  |   __|  _  |  |  |  |\
              /_____|_____|__|__|_____|__|___\____|________| |  Durr....
              \_____________________________________________\|  v 0.5

OVERVIEW:

Durdraw is an ASCII and ANSI drawing program for Linux and MacOS X that
supports frame-based animation, attempting to make ANSI and ASCII art
animation work more like a traditional animation studio.

It has editing features such as importing ascii files to frames, duplicating
and deleting frames, flipping between frames, and frames-per-second speed
control during playback.

Files can be loaded and saved in ASCII (.asc, .txt) or in DUR animation
format. Files can also be saved in animated GIF (with FPS accuracy), PNG and ANSI
formats.

REQUIREMENTS:

* Python 2.5.2 or higher (not tested with older versions)
* Python Ncurses

RECOMMENDED:

* A terminal and font that supports Code Page 463 (US-Latin-1, Western ASCII,
  etc) is recommended for IBM-PC Extended ASCII. See PRO TIPS section below.
* Animated GIF requires the following ncurses modules:
    PIL
    images2gif
* PNG and Animated GIF requires that Ansilove be in your path.
    Ansilove can be found at: http://ansilove.sourceforge.net/

USAGE:

usage: durdraw [-h] [-p PLAY [PLAY ...]] [-q | -w] [-V] [filename]

positional arguments:
  filename              .dur or ascii file to load

optional arguments:
  -h, --help            show this help message and exit
  -p PLAY [PLAY ...], --play PLAY [PLAY ...]
                        Just play .dur file or files, then exit
  -q, --quick           Skip startup screen
  -w, --wait            Pause at startup screen
  -V, --version         Show version number and exit

COMMANDS:

                /\ |\ |||\  /|            .-.  _| . _|_
               /--\| \||| \/ | ()         |/_ (_| |  |
      alt-k - next frame                  alt-' - delete current line
      alt-j - prev frame                  alt-/ - insert line
      alt-n - new frame from current      alt-, - delete current column.
      alt-N - new empty frame             alt-. - insert new column
      alt-p - play animation (up/down     alt-c - clear canvas/movie
              change FPS, any other       alt-m - mark selection for
              key stops playback)                 copy/paste/cut/move *
      alt-d - delete current frame        F1-F10 - insert character
   ..  ..----------------------------------------------------------..  ..
           alt-s - save, alt-o - open, alt-h - help, alt-q - quit
              alt-up - next fg color, alt-down - prev fg color
            alt-right - next bg color, alt-left - prev bg color
        alt-z - undo, alt-r - redo, alt-D - set current frame delay

PRO TIPS:

    * If ALT doesn't work, use ESC or configure your terminal to map ALT to
      META.

    * The mouse can be used for moving the cursor (even over SSH!) if your
      terminal supports Xterm mouse reporting. (In iTerm2 this is under
      Profiles, Terminal and Terminal Emulation.)

    * The recommended terminal for Linux is rxvt with the VGA font. To get
      ANSI extended characters (AKA code page 437, IBM-PC font, etc) working
      in Linux, follow these instructions for setting up rxvt:

http://techtinkering.com/2010/02/14/getting-colour-ansi-emulation-to-work-properly-when-connecting-to-a-bbs-with-telnet-under-linux/

    * Good terminals to use in Mac OS X are the default Terminal.app and
      iTerm.  To get extended characters working in MacOS X Terminal, follow
      these instructions (similar settings can be used for iTerm2):

1: Install dos437.ttf font (included) by double-clicking it.
2: Create a profile in Terminal Preferences/Settings with the following
   settings:
    + In Text tab, Font set to dos437 (I like 9pt) and "Display ANSI colors"    
      and "Use bright colors for bold text" are checked
    + In Keyboard tab, "Use option as meta key" selected
    + In "Advanced" tab, Character encoding set to "Western (ASCII)"
    + Set background color to black (low or no transprency) and foreground
      color to white

    * If extended characters are not working in gnu screen, try running the
      following screen command (by pressing ctrl-a and typing):
        :utf8 off off
      then type "clrl-a l" to redraw the window.
        
CREDITS:

Sam Foster (http://cmang.org)

Homepage: http://cmang.org/durdraw

LEGAL:

Durdraw is Copyright 2009-2014 Sam Foster (cmang), all rights reserved

Permission to use, copy, modify, and distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

License for dos437.ttf font:
Copyright (c) 2011 joshua stein <jcs@jcs.org>

Permission to use, copy, modify, and distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

