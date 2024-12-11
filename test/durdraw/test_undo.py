from collections import deque

import durdraw.durdraw_undo as undo

class TestUndo:

    def test_push(self):
        r = undo.UndoRegister()
        r.push(1)

        assert r.state == 1
        assert r.undoBuf == deque([1])
        assert r.redoBuf == deque()

    def test_undo(self):
        r = undo.UndoRegister(1)
        r.push(2)
        r.push(3)

        assert r.state == 3
        assert r.undo() == 3

        assert r.state == 2
        assert r.undoBuf == deque([1,2])
        assert r.redoBuf == deque([3])
