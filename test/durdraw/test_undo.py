from collections import deque, namedtuple

import durdraw.durdraw_undo as undo

class TestUndo:

    def test_push(self):
        'initial state is set, push adds new state to the undo buffer'

        r = undo.UndoRegister(1)
        assert r.state == 1

        r.push(2)
        assert r.state == 2
        assert r.undoBuf, r.redoBuf == (deque([1,2]), deque())

    def test_undo(self):
        'undo returns the previous state, and removes it from the undo buffer'

        r = undo.UndoRegister(1)
        r.push(2)
        r.push(3)
        assert r.state == 3

        assert r.undo() == 3
        assert r.state == 2
        assert r.undoBuf, r.redoBuf == (deque([1,2]), deque([3]))

    def test_undo_no_history(self):
        'undo returns None if there is no history to undo'

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
        'redo returns the next state, and removes it from the redo buffer'

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
        'redo returns None if there is no history to redo'

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
        'redo buffer is cleared when a new state is pushed after undo'

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

    def test_complex_states(self):
        'undo and redo with more complex states'
        state = namedtuple('state', 'a b c')
        s0, s1, s2 = state(0,0,0), state(1,2,3), state(4,5,6)

        r = undo.UndoRegister(s1)
        r.push(s1)

        assert r.state == s1
        assert r.undoBuf, r.redoBuf == (deque([s0, s1]), deque())

        r.push(s2)
        assert r.state == s2
        assert r.undoBuf, r.redoBuf == (deque([s0, s1, s2]), deque())

