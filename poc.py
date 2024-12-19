#!/usr/bin/env python3

from collections import deque
import curses
import time

import line_profiler

#python3 -m pip install git+https://github.com/tmck-code/pp
from pp import log

# NOTE: set this to DEBUG to see the debug logs
LOG = log.getLogger('poc', filename='poc.log', level='INFO')

class UndoRegister:
    def __init__(self, initial_state=None):
        self.undo_buf, self.redo_buf = deque(), deque()
        if initial_state:
            self.undo_buf.append(initial_state)

    @line_profiler.profile
    def push(self, el):
        if self.redo_buf:
            self.redo_buf.clear()
        self.undo_buf.append(el)
        # LOG.debug('push', {'undo_buf': self.undo_buf, 'redo_buf': self.redo_buf})

    @line_profiler.profile
    def undo(self):
        if self.can_undo:
            self.redo_buf.appendleft(self.undo_buf.pop())
            # LOG.debug('undo', {'undo_buf': self.undo_buf, 'redo_buf': self.redo_buf})
            return self.redo_buf[0]

    @line_profiler.profile
    def redo(self):
        if self.can_redo:
            self.undo_buf.append(self.redo_buf.popleft())
            # LOG.debug('redo', {'undo_buf': self.undo_buf, 'redo_buf': self.redo_buf})
            return self.undo_buf[-1]

    @property
    @line_profiler.profile
    def can_undo(self):
        return bool(self.undo_buf)

    @property
    @line_profiler.profile
    def can_redo(self):
        return bool(self.redo_buf)

@line_profiler.profile
def move_cursor(stdscr, x, y, c):
    '''
    Moves the cursor in the terminal window, based on the arrow key pressed.
    Doesn't allow the cursor to go out of the window boundaries, will wrap around.
    '''
    if   c == curses.KEY_LEFT:  stdscr.move(y,                        max(x-1, 0))
    elif c == curses.KEY_RIGHT: stdscr.move(y,                        min(x+1, curses.COLS-1))
    elif c == curses.KEY_DOWN:  stdscr.move(min(y+1, curses.LINES-1), x)
    elif c == curses.KEY_UP:    stdscr.move(max(y-1, 0),              x)

@line_profiler.profile
def undo_char(stdscr, undo_register):
    '''
    Performs an undo operation:
    - pop the last undo operation from the undo register
    - restore the previous state for the pixel at the x,y coordinates
    - move the cursor to those x,y coordinates
    '''
    if undo_register.can_undo:
        x, y, prev_char, _next_char = undo_register.undo()
        stdscr.addch(y, x, prev_char)
        stdscr.move(y, x)

@line_profiler.profile
def redo_char(stdscr, undo_register):
    '''
    Performs a redo operation (reverses an undo operation):
    - pop the last redo operation from the undo register
    - restore the next state for the pixel at the x,y coordinates
    - move the cursor to those x,y coordinates
    '''
    if undo_register.can_redo:
        x, y, _prev_char, next_char = undo_register.redo()
        stdscr.addch(y, x, next_char)

@line_profiler.profile
def insert_char(stdscr, undo_register, x, y, c):
    '''
    Inserts a character at the current cursor position, and
    pushes this action to the undo register, with the previous and current pixel states
    '''
    prev_char = stdscr.inch(y, x)
    stdscr.addch(c)
    undo_register.push((x, y, prev_char, c))

ARROW_KEYS = set([curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_DOWN, curses.KEY_UP])

@line_profiler.profile
def process_input(stdscr, undo_register, x, y, c):
    '''
    Processes the input character, and performs the corresponding action.
    - moves the cursor if an arrow key is pressed
    - performs undo/redo if 'u' or 'r' is pressed
    - inserts a character if any other key is pressed
    '''
    # LOG.debug('processing input', {'key': c, 'x': x, 'y': y})
    # start_time = time.time()

    if   c in ARROW_KEYS: move_cursor(stdscr, x, y, c)
    elif c == ord('u'):   undo_char(stdscr, undo_register)
    elif c == ord('r'):   redo_char(stdscr, undo_register)
    elif c == ord('U'):   [undo_char(stdscr, undo_register) for _ in range(10)]
    elif c == ord('R'):   [redo_char(stdscr, undo_register) for _ in range(10)]
    elif c < 256:         insert_char(stdscr, undo_register, x, y, c)
    else:                 LOG.debug('unhandled key', {'key': c})

    # end_time = time.time()
    # LOG.debug('processed input', {'key': c, 'x': x, 'y': y, 'elapsed': (end_time-start_time)*10**6, 'unit': 'us'})

@line_profiler.profile
def get_input(stdscr, undo_register):
    '''
    Main loop to get character (keyboard) input from the user, and process it.
    Instantly quits if "q" is pressed
    '''
    while True:
        (y, x), c = stdscr.getyx(), stdscr.getch()
        if c == ord('q'):
            break
        process_input(stdscr, undo_register, x, y, c)

def pad(stdscr):
    '''
    Main function to initialize the terminal window, and start the main loop.
    - prints a simple help message
    - moves the cursor to the center of the window
    - starts the main loop
    '''
    help_lines = ['type any key!', 'use arrow keys to navigate', 'u/r to undo/redo', 'q to quit', 'U/R for MEGA 10x undo/redo!']
    for i, line in enumerate(help_lines):
        stdscr.addstr(i, 0, line, curses.A_REVERSE)

    stdscr.move((curses.LINES-1)//2, (curses.COLS-1)//2)
    stdscr.refresh()

    get_input(stdscr, UndoRegister())

curses.wrapper(pad)

