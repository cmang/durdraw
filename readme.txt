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
      alt-k - next frame               |  esc-up - delete current line
      alt-j - prev frame               |  esc-down - insert line
      alt-n - new frame from current   |  esc-left - delete current column.
      alt-p - play animation (up/down  |  esc-right - insert new column
              change FPS, any other    |  alt-m - mark selection for
              key stops playback)      |          copy/paste/cut/move *
      alt-d - delete current frame     |  alt-c - clear canvas/movie
   ..  ..------------------------------|  alt-s - save, alt-o - open
                                       |  alt-q - quit
                                       `----------------------------..  ..
    PRO TIP:
    if ALT doesn't work, use ESC or configure terminal to map ALT to META

Homepage: http://bitbucket.org/sfoster/durdraw/

Credits:

Sam Foster (http://cmang.org)

