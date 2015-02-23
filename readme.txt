                  __                __
                _|  |__ __ _____ __|  |_____ _____ __ __ __
               / _  |  |  |   __|  _  |   __|  _  |  |  |  |\
              /_____|_____|__|__|_____|__|___\____|________| |  Durr....
              \_____________________________________________\|  v 0.6

OVERVIEW:

Durdraw is an ASCII and ANSI drawing program for Linux and MacOS X that
supports frame-based animation, attempting to make ANSI and ASCII art
animation work more like a traditional animation studio.

Durdraw can also be used to view or playback .dur animation files, even from
shell scripts.

It has editing features such as importing ascii files to frames, duplicating
and deleting frames, flipping between frames, and frames-per-second speed
control during playback. It supports the mouse.

Files can be loaded and saved in ASCII (.asc, .txt) or in DUR animation
format. Files can also be saved in animated GIF (with FPS accuracy), PNG and ANSI
formats.

REQUIREMENTS:

* Python 2.5.2 or higher (not tested with older versions)
* Python Ncurses

RECOMMENDED:

* A terminal and font that supports Code Page 463 (US-Latin-1, Western ASCII,
  etc) is recommended for IBM-PC Extended ASCII. See optional instructions
  below for using mrxvt.
* Animated GIF requires the following Python modules:
    PIL
    images2gif
* PNG and Animated GIF requires that Ansilove be in your path.
    Ansilove can be found at: http://ansilove.sourceforge.net/

BASIC INSTALLATION:

* Copy the file "durdraw" to a nice place like /usr/local/bin/
* Copy the file "durhelp.dur" to /usr/local/share/durdraw/ or ~/.dur/

OPTIONAL INSTALLATION:

For a better durdraw terminal in Linux:

* Install mrxvt
* Give mrxvt IBM-PC colors by copying the contents of Xdefaults in to your own ~/.Xdefaults file
* Install vga.pcf by copying it to /usr/share/fonts/X11/misc and then running these commands:
    $ mkfontdir /usr/share/fonts/X11/misc/
    $ xset fp rehash

For PNG and animated GIF export:

* Install PIL, images2gif and Ansilove (see RECOMMENDED section above)

COMMAND LINE USAGE:

usage: durdraw [-h] [-p PLAY [PLAY ...]] [-q | -w | -x TIMES] [--nomouse]
               [-u UNDOSIZE] [-V]
               [filename]

positional arguments:
  filename              .dur or ascii file to load

optional arguments:
  -h, --help            show this help message and exit
  -p PLAY [PLAY ...], --play PLAY [PLAY ...]
                        Just play .dur file or files, then exit
  -q, --quick           Skip startup screen
  -w, --wait            Pause at startup screen
  -x TIMES, --times TIMES
                        Play X number of times (requires -p)
  --nomouse             Disable mouse support
  -u UNDOSIZE, --undosize UNDOSIZE
                        Set the number of undo history states - default is
                        100. More requires more RAM, less saves RAM.
  -V, --version         Show version number and exit

INTERACTIVE USAGE/COMMANDS:

      alt-k - next frame                  alt-' - delete current line
      alt-j - prev frame                  alt-/ - insert line
      alt-n - iNsert current frame clone  alt-, - delete current column.
      alt-N - appeNd empty frame          alt-. - insert new column
      alt-p - start/stop Playback         alt-c - Clear canvas/movie
      alt-d - Delete current frame        alt-m - Mark selection
      alt-D - set current frame Delay     F1-F10 - insert character
      alt-+/alt-- increase/decrease FPS   alt-z - undo
      alt-M - Move current frame          alt-r - Redo
      alt-up - next fg color              alt-s - Save
      alt-down - prev fg color            alt-o - Open
      alt-right - next bg color           alt-q - Quit
      alt-left - prev bg color            alt-h - Help
      alt-R - set playback/edit Range     alt-g - Go to frame #

Can use ESC or META instead of ALT

OTHER TIPS:

    * The mouse can be used for moving the cursor (even over SSH!) if your
      terminal supports Xterm mouse reporting. (In iTerm2 this is under
      Profiles, Terminal and Terminal Emulation.)

    * If extended characters are not working in gnu screen, try running the
      following screen command (by pressing ctrl-a and typing):
        :utf8 off off
      then type "clrl-a l" to redraw the window.

    * Good terminals to use in Mac OS X are the default Terminal.app and
      iTerm.  To get extended characters working in MacOS X Terminal, follow
      these instructions (similar settings can be used for iTerm2):

1: Install dos437.ttf font (included) by double-clicking it.
2: Create a profile in Terminal Preferences/Settings with the following
   settings (similar settings can be applied in iTerm):
    + In Text tab, Font set to dos437 (I like 9pt) and "Display ANSI colors"    
      and "Use bright colors for bold text" are checked
    + In Keyboard tab, "Use option as meta key" selected
    + In "Advanced" tab, Character encoding set to "Western (ASCII)"
    + Set background color to black (low or no transprency) and foreground
      color to white

        
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

The vga.pcf font was taken from the Dosemu project and appears to be in
the public domain. Further discussion on its copyright status can be found
at http://www.dosemu.org/docs/misc/COPYING.html

