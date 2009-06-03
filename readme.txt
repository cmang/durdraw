        __                 __
      _|  |__ __ _____ ___|  |_____ _____ __ __ __
     / _  |  |  |   __|  _   |   __|  _  |  |  |  |\
    /_____|_____|__|__|______|__|___\____|________| |  Durr....
    \______________________________________________\|  v 0.1

Introduction:

Durdraw is a program for drawing ascii art.  It is designed with the goal of
being reliable and friendly to common Unix terminals like Xterm, Putty, etc. 

!! Important note !!:  Currently if the terminal size goes above 80x24 there
is a risk of Durdraw crashing and your work being lost.  I recommend making
your window 80x25 or larger.
 
The interface is in the spirit of TheDraw and Aciddraw for MS-DOS, although
high ascii symbols are not (yet?) supported. (Unicode?)

Derdraw requires a Unix-like systems with a fairly recent version of Python.

Usage:

You can use the arrow keys to move the cursor and the keyboard to insert
and delete characters.

Commands (Alt can be substituted with ESC):

Alt-O       - open a file
Alt-S       - Save Current Drawing
Alt-Up      - Delete Current Line
Alt-Down    - Insert New Line
Alt-Left    - Delete Column
Alt-Right   - Insert Column
Ctrl-L      - Refresh the Screen
Alt-Q       - Quit

Tips:

Know the file name you're going to load - you have to type it in.
As stated above, use a window 80x24 or larger.
Submit patches if you have them. :)

Homepage: http://bitbucket.org/sfoster/durdraw/

Credits:

Sam Foster (http://cmang.org)

