#!/usr/bin/env python3

from collections import deque
import curses
from curses import wrapper

#python3 -m pip install git+https://github.com/tmck-code/pp
from pp import log

LOG = log.getLogger('poc', filename='poc.log', level='DEBUG')

class UndoRegister:
    __slots__ = ['undoBuf', 'redoBuf', 'logger']

    def __init__(self, initial_state=None):
        self.undoBuf, self.redoBuf = deque(), deque()
        if initial_state:
            self.undoBuf.append(initial_state)

    def push(self, el):
        if self.redoBuf:
            self.redoBuf.clear()
        self.undoBuf.append(el)
        LOG.debug('push', {'undoBuf': self.undoBuf, 'redoBuf': self.redoBuf})

    def undo(self):
        if not self.can_undo:
            return None
        self.redoBuf.appendleft(self.undoBuf.pop())
        LOG.debug('undo', {'undoBuf': self.undoBuf, 'redoBuf': self.redoBuf})
        return self.redoBuf[0]

    def redo(self):
        if not self.can_redo:
            return None
        self.undoBuf.append(self.redoBuf.popleft())
        LOG.debug('redo', {'undoBuf': self.undoBuf, 'redoBuf': self.redoBuf})
        return self.undoBuf[-1]

    @property
    def can_undo(self):
        return bool(self.undoBuf)

    @property
    def can_redo(self):
        return bool(self.redoBuf)

    @property
    def state(self):
        return self.undoBuf[-1]

    @property
    def buffers(self):
        return self.undoBuf, self.redoBuf

def move_cursor(stdscr, x, y, c):
    match c:
        case curses.KEY_LEFT:
            stdscr.move(y, max(x-1, 0))
        case curses.KEY_RIGHT:
            stdscr.move(y, min(x+1, curses.COLS-1))
        case curses.KEY_DOWN:
            stdscr.move(min(y+1, curses.LINES-1), x)
        case curses.KEY_UP:
            stdscr.move(max(y-1, 0), x)

def undo_char(stdscr, undo_register):
    if undo_register.can_undo:
        (x, y), (prev_char, next_char) = undo_register.undo()
        stdscr.addch(y, x, prev_char)
        stdscr.refresh()
        stdscr.move(y, x)

def redo_char(stdscr, undo_register):
    if undo_register.can_redo:
        (x, y), (prev_char, next_char) = undo_register.redo()
        stdscr.addch(y, x, next_char)
        stdscr.refresh()

def insert_char(stdscr, undo_register, x, y, c):
    (y, x), prev_char = stdscr.getyx(), stdscr.inch(y, x)
    stdscr.addch(c)
    undo_register.push(((x, y), (prev_char, c)))
    stdscr.refresh()

def get_input(stdscr, undo_register):
    # curses.echo()
    while True:
        (y, x), c = stdscr.getyx(), stdscr.getch()

        if c == ord('q'):
            break
        elif c == ord('u'):
            undo_char(stdscr, undo_register)
        elif c == ord('r'):
            redo_char(stdscr, undo_register)
        elif c in [curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_DOWN, curses.KEY_UP]:
            move_cursor(stdscr, x, y, c)
        elif c < 256:
            insert_char(stdscr, undo_register, x, y, c)
        else:
            LOG.debug('unhandled key', {'key': c})

def pad(stdscr):
    help_lines = [
        'type any key!', 'use arrow keys to navigate',
        'u/r to undo/redo', 'q to quit',
    ]
    for i, line in enumerate(help_lines):
        stdscr.addstr(i, 0, line, curses.A_REVERSE)
    stdscr.move((curses.LINES-1)//2, (curses.COLS-1)//2)

    stdscr.refresh()
    get_input(stdscr, UndoRegister())

wrapper(pad)

