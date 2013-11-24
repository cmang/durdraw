                  __                __
                _|  |__ __ _____ __|  |_____ _____ __ __ __
               / _  |  |  |   __|  _  |   __|  _  |  |  |  |\
              /_____|_____|__|__|_____|__|___\____|________| |  Durr....
              \_____________________________________________\|  v 0.2

Durdraw is an ASCII drawing program that supports frame-based animation, to make
ASCII animation work more like a traditional animation studio.

It supports importing ascii files to frames, duplicating and deleting frames,
flipping between frames, and frames-per-second control during playback.

Files can be loaded and saved in ASCII (.asc, .txt) or in proprietary DUR
animation formats.

To open a .dur or .asc file from the command line, use:

durddraw filename.dur
or:
durdraw filaneme.asc

COMMANDS:
            ..________________________________________________..
                /\ |\ |||\  /|         |  .-.  _| . _|_
               /--\| \||| \/ | ()      |  |/_ (_| |  |
      alt-k - next frame               |  alt-up - delete current line
      alt-j - prev frame               |  alt-down - insert line
      alt-n - new frame from current   |  alt-left - delete current column.
      alt-p - play animation (up/down  |  alt-right - insert new column
              change FPS, any other    |  alt-m - mark selection for
              key stops playback)      |          copy/paste/cut/move *
      alt-d - delete current frame     :  alt-c - clear canvas/movie
   ..  ..----------------------------------------------------------..  ..

           alt-s - save, alt-o - open, alt-h - help, alt-q - quit

PRO TIPS:

    * If ALT doesn't work, use ESC or configure your terminal to map ALT to
      META.

    * To get extended characters (AKA code page 437, ibm-pc characters, DOS
      characters, etc) working in Linux, follow these instructions (I recommend
      using 'vga' font instead of 'vga11x19' with rxvt):

http://techtinkering.com/2010/02/14/getting-colour-ansi-emulation-to-work-properly-when-connecting-to-a-bbs-with-telnet-under-linux/

    * To get extended characters (AKA code page 437, ibm-pc characters, DOS
      characters, blocks, etc) working in MacOS X Terminal.app, follow these
      instructions:

1: Install dos437.ttf font (included) by doucle-clicking it.
2: Create a profile in Terminal Preferences/Settings with the following
   settings:
    + In Text tab, Font set to dos437 (I like 9pt) and "Display ANSI colors"    
      checked
    + In Keyboard tab, "Use option as meta key" selected
    + In "Advanced" tab, Character encoding set to "Western (ASCII)"
    + Set background color to black (low or no transprency) and foreground
      color to white

Homepage: http://bitbucket.org/sfoster/durdraw/

Credits:

Sam Foster (http://cmang.org)


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

