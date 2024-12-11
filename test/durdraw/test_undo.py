from collections import deque

import durdraw.durdraw_undo as undo

class TestUndo:

    def test_push(self):
        r = undo.UndoRegister(1)
        assert r.state == 1

        r.push(2)
        assert r.state == 2
        assert r.undoBuf, r.redoBuf == (deque([1,2]), deque())

    def test_undo(self):
        r = undo.UndoRegister(1)
        r.push(2)
        r.push(3)
        assert r.state == 3

        assert r.undo() == 3
        assert r.state == 2
        assert r.undoBuf, r.redoBuf == (deque([1,2]), deque([3]))

    def test_undo_no_history(self):
        r = undo.UndoRegister(1)
        assert r.state == 1

        # cannot undo if only initial state
        assert r.undo() == None
        assert r.undoBuf, r.redoBuf == (deque([1]), deque())

        # push a new state
        r.push(2)
        assert r.state == 2
        assert r.undoBuf, r.redoBuf == (deque([1,2]), deque())

        # then undo that state
        assert r.undo() == 2
        assert r.state == 1
        assert r.undoBuf, r.redoBuf == (deque([1]), deque([2]))

        # cannot undo again, only state
        assert r.undo() == None

    def test_redo(self):
        r = undo.UndoRegister(1) # initial state, cannot be undone
        r.push(2) # 1st change
        r.push(3) # 2nd change
        assert r.state == 3

        # undo twice, to the beginning of the undo buf
        assert r.undo() == 3
        assert r.undo() == 2

        # check the state
        assert r.state == 1
        assert r.undoBuf, r.redoBuf == (deque([1]), deque([2,3]))

        # now redo twice
        assert r.redo() == 2
        assert r.state == 2
        assert r.undoBuf, r.redoBuf == (deque([1,2]), deque([3]))

        assert r.redo() == 3
        assert r.state == 3
        assert r.undoBuf, r.redoBuf == (deque([1,2,3]), deque())

    def test_redo_no_history(self):
        r = undo.UndoRegister(1)
        r.push(2)

        # cannot redo if no undos were made
        assert r.redo() == None

        # undo
        assert r.undo() == 2
        assert r.state == 1
        assert r.undoBuf, r.redoBuf == (deque([1]), deque([2]))

        # now redo
        assert r.redo() == 2
        assert r.state == 2
        assert r.undoBuf, r.redoBuf == (deque([1,2]), deque())

        # cannot redo again
        assert r.redo() == None

    def test_redo_push(self):
        r = undo.UndoRegister(1)
        r.push(2)
        r.push(3)

        # undo twice, to the beginning of the undo buf
        assert r.undo() == 3
        assert r.undo() == 2

        # check the state
        assert r.state == 1
        assert r.undoBuf, r.redoBuf == (deque([1]), deque([2,3]))

        # now push a new state 😱
        # this should push a new state, and clear the redo buffer
        r.push(4)
        assert r.state == 4
        assert r.undoBuf, r.redoBuf == (deque([1,4]), deque())

        # cannot redo if a new state has been pushed
        assert r.redo() == None
        assert r.state == 4
        assert r.undoBuf, r.redoBuf == (deque([1,4]), deque())
