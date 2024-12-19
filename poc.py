#!/usr/bin/env python3

from collections import deque
import curses
import time

import line_profiler

#python3 -m pip install git+https://github.com/tmck-code/pp
from pp import log

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
    if   c == curses.KEY_LEFT:  stdscr.move(y,                        max(x-1, 0))
    elif c == curses.KEY_RIGHT: stdscr.move(y,                        min(x+1, curses.COLS-1))
    elif c == curses.KEY_DOWN:  stdscr.move(min(y+1, curses.LINES-1), x)
    elif c == curses.KEY_UP:    stdscr.move(max(y-1, 0),              x)

@line_profiler.profile
def undo_char(stdscr, undo_register):
    if undo_register.can_undo:
        x, y, prev_char, _next_char = undo_register.undo()
        stdscr.addch(y, x, prev_char)
        stdscr.move(y, x)

@line_profiler.profile
def redo_char(stdscr, undo_register):
    if undo_register.can_redo:
        x, y, _prev_char, next_char = undo_register.redo()
        stdscr.addch(y, x, next_char)

@line_profiler.profile
def insert_char(stdscr, undo_register, x, y, c):
    prev_char = stdscr.inch(y, x)
    stdscr.addch(c)
    undo_register.push((x, y, prev_char, c))

ARROW_KEYS = set([curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_DOWN, curses.KEY_UP])

@line_profiler.profile
def process_input(stdscr, undo_register, x, y, c):
    # LOG.debug('processing input', {'key': c, 'x': x, 'y': y})
    # start_time = time.time()

    if   c == ord('q'):     return
    elif c == ord('u'):     undo_char(stdscr, undo_register)
    elif c == ord('r'):     redo_char(stdscr, undo_register)
    elif c in ARROW_KEYS:   move_cursor(stdscr, x, y, c)
    elif c < 256:           insert_char(stdscr, undo_register, x, y, c)
    else:                   LOG.debug('unhandled key', {'key': c})

    # LOG.debug('processed input', {'key': c, 'x': x, 'y': y, 'elapsed': (time.time()-start_time)*10**6, 'unit': 'us'})

@line_profiler.profile
def get_input(stdscr, undo_register):
    while True:
        (y, x), c = stdscr.getyx(), stdscr.getch()
        if c == ord('q'):
            break
        process_input(stdscr, undo_register, x, y, c)

def pad(stdscr):
    # print a simple help message
    help_lines = ['type any key!', 'use arrow keys to navigate', 'u/r to undo/redo', 'q to quit']
    for i, line in enumerate(help_lines):
        stdscr.addstr(i, 0, line, curses.A_REVERSE)
    # move the cursor to the center to start
    stdscr.move((curses.LINES-1)//2, (curses.COLS-1)//2)
    stdscr.refresh()

    # start the main loop
    get_input(stdscr, UndoRegister())

curses.wrapper(pad)

