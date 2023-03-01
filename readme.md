Durdraw
=======

                  __                __
                _|  |__ __ _____ __|  |_____ _____ __ __ __
               / _  |  |  |   __|  _  |   __|  _  |  |  |  |\
              /_____|_____|__|__|_____|__|___\____|________| |  Durr....
              \_____________________________________________\|  v 0.18.1


![durdraw-help-screen-256color](https://user-images.githubusercontent.com/261501/214016536-9413463f-2fe4-4298-8022-95daeabbe894.png)

## OVERVIEW:

Durdraw is an ASCII, ANSI and Unicode art editor for UNIX-like systems (Linux, 
macOS, etc). It runs in the terminal and supports color and frame-based
animation, attempting to make ANSI and ASCII art animation work more like
a traditional animation studio. It supports 256 color modes when available.

Durdraw is heavily inspired by classic ANSI editing software for MS-DOS and
Windows, such as TheDraw, Aciddraw and Pablodraw.

Some animation features include importing ascii files to frames, duplicating
and deleting frames, switching between frames, and frames-per-second speed
control during playback. It supports both the mouse and keyboard.

Files can be saved in DUR animation format, or exported in ASCII (.asc, .txt),
ANSI (.ans), JSON, GIF and PNG formats.

## SCREENSHOTS AND EXAMPLES:

![dopetrans3](https://user-images.githubusercontent.com/261501/210064369-4c416e85-12d0-47aa-b182-db5435ae0c78.gif)
![durdraw-screenshot](https://user-images.githubusercontent.com/261501/142838691-9eaf58b0-8a1f-4636-a41a-fe8617937d1d.gif)
![durdraw-linux-unicode-ansi](https://user-images.githubusercontent.com/261501/161380487-ac6e2b5f-d44a-493a-ba78-9903a6a9f1ca.png)
![eye](https://user-images.githubusercontent.com/261501/210064343-6e68f88d-9e3e-415a-9792-a38684231ba0.gif)
![cm-doge](https://user-images.githubusercontent.com/261501/210064365-e9303bee-7842-4068-b356-cd314341098b.gif)
![bsd-color-new](https://user-images.githubusercontent.com/261501/210064354-5c1c2adc-06a3-43c5-8e21-30b1a81db315.gif)

## REQUIREMENTS:

* Python 3
* Linux, macOS, or other Unix-like System

## INSTALLATION:

1: Download and extract, or use git to download:

```
   git clone https://github.com/cmang/durdraw.git  
   cd durdraw 
```

2: Install using pip:

```
    pip install .
```

Or run the installer:

```
   python3 setup.py install
```

You should now be able to run `durdraw`

## RUNNING WITHOUT INSTALLING

You may need to install the "PIL" or "pillow" python module first:

```
    pip3 install pillow
```

Then you can run Durdraw with:

```
    ./start-durdraw
```

To look at some included example animations:

```
    ./start-durdraw -p examples/*.dur
```

## COMMAND LINE USAGE:

You can play a .dur file or series of .dur files with:

```
    $ durdraw -p filename.dur
    $ durdraw -p file1.dur file2.dur file3.dur ...
```

Other command-line options:

<pre>

usage: start-durdraw [-h] [-p PLAY [PLAY ...]] [-q | -w | -x TIMES] [--256color | --16color] [-b]
                     [-W WIDTH] [-H HEIGHT] [-m] [--nomouse] [-A] [-u UNDOSIZE] [-V] [--debug]
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
  --256color            Try 256 color mode
  --16color             Try 16 color mode
  -b, --blackbg         Use a black background color instead of terminal default
  -W WIDTH, --width WIDTH
                        Set canvas width
  -H HEIGHT, --height HEIGHT
                        Set canvas height
  -m, --max             Maximum canvas size for terminal (overrides -W and -H)
  --nomouse             Disable mouse support
  -A, --ansi            IBM-PC ANSI Art Mode - Use F1-F10 keys for Code Page 437 extended ASCII (IBM-
                        PC) block characters
  -u UNDOSIZE, --undosize UNDOSIZE
                        Set the number of undo history states - default is 100. More requires more
                        RAM, less saves RAM.
  -V, --version         Show version number and exit

</pre>

## INTERACTIVE USAGE/EDITING:

Use the arrow keys (or mouse) and other keys to edit, much like a text editor.
Also:

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
      alt-R - set playback/edit Range     alt-pgdn - next character set
      alt-g - Go to frame #               alt-pgup - prev character set

Can use ESC or META instead of ALT

## OTHER TIPS:

    * The mouse can be used for moving the cursor (even over SSH) and
      clicking buttons, if your terminal supports Xterm mouse reporting.
      In iTerm2 this is under Profiles, Terminal and Terminal Emulation.

    * If IBM-PC characters (-A) are not working in gnu screen, try running the
      following screen command (by pressing ctrl-a and typing):
        :utf8 off off
      then type "clrl-a l" to redraw the window.
      Also see "OPTIONAL INSTALLATION" notes below

## OPTIONAL INSTALLATION:

For PNG and animated GIF export, install Ansilove (https://ansilove.org/) and make sure it is is in your path. (Recommended)

If you want to try making animated IBM-PC/MS-DOS ANSI art with durdraw, you
need a terminal and font that supports ASCII encoding and IBM's Code Page 437.
You can find fonts in the "extras" directory for this purpose.

Note that ANSI art character support is experimental (see FAQ).

In Linux/X11, here is one possible way to set up a terminal for IBM-PC ANSI art:

* Install mrxvt
* Install vga.pcf by copying it to /usr/share/fonts/X11/misc and then running
  these commands. This may be different on your OS:
    $ mkfontdir /usr/share/fonts/X11/misc/
    $ xset fp rehash
* Give mrxvt IBM-PC colors by copying the contents of Xdefaults into your own
  ~/.Xdefaults file. You can create ~/.Xdefaults if it does not exist.
* Launch mrxvt with: mrxvt -fn vga -bg black -fg grey

If you are using macOS or MacOS X and want IBM-PC ANSI art support in
Terminal.app:

1. Install dos437.ttf font (included) by double-clicking it.
2. Create a profile in Terminal Preferences/Settings with the following
   settings (similar settings can be applied in iTerm):
    * In Text tab, Font set to dos437 (I like 9pt) and "Display ANSI colors"    
      and "Use bright colors for bold text" are checked
    * In Keyboard tab, "Use option as meta key" selected
    * In "Advanced" tab, Character encoding set to "Western (ASCII)"
    * Set background color to black (low or no transprency) and foreground
      color to white

Once this is setup, pass "-A" to durdraw's command-line to allow you to use
F1-F12 to input ANSI block characters. 

## FAQ

#### Q: Don't TheDraw and some other programs already do ANSI animation?
A: Yes, but traditional ANSI animation does not provide any control over timing, instead relying on terminal baud rate to control the speed. This does not work well on modern systems without baud rate emulation. DurDraw gives the artist fine control over frame rate, and delays per frame. Traditional ANSI animation also updates the animation one character at a time, while DurDraw updates the animation a full frame at a time. This makes it less vulnerable to visual corruption from things like errant terminal characters, resized windows, line noise, etc. Finally, unlike TheDraw, which requires MS-DOS, Durdraw runs in modern Unicode terminals.

#### Q: Can I run Durdraw in Windows?
A: Short answer: It's not supported, but it seems to work fine in the Windows Subsystem for Linux (WSL). Long answer: Some versions run fine in Windows Command Prompt, Windows Terminal, etc, without WSL, but it's not tested or supported. If you want to help make Durdraw work better in Windows, please help by testing, submitting bug reports and submitting patches.

#### Q: Can I run Durdraw on Amiga, MS-DOS, Classic MacOS, iOS, Android, etc?
A: Probably not easily. DurDraw requires Python 3 and Ncurses. If your platform can support these, it will probably run. However, the file format for Durdraw movies is a plain text JSON format. It should be possible to support this format in different operating systems and in different applications.

#### Q: Does DurDraw support IBM-PC ANSI art?
A: Yes - Kind of. Durdraw can support IBM-PC (Code Page 437) extended ASCII characters using the -A command-line option, and can export ANSI files. However, ANSI importing is not currently supported. Please see the "OPTIONAL INSTALLATION" section above for more details. If you do not pass the -A command-line option, then Unicode block characters similar to IBM-PC block characters are enabled by default.

### CREDITS:

Developer: Sam Foster

Home page: http://durdraw.org

Development: https://github.com/cmang/durdraw

### LEGAL:

Durdraw is Copyright (c) 2009-2023 Sam Foster <samfoster@gmail.com>. All rights reserved.

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

