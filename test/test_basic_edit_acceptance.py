from unittest import TestCase

import sys
sys.path.append('../PyRoom')

# mock out gettext
import __builtin__
__builtin__._ = lambda str: str


from PyRoom.preferences import PyroomConfig
from PyRoom.basic_edit import BasicEdit
from PyRoom.undoable_buffer import UndoableBuffer


class TestBasicEditAcceptance(TestCase):

    def test_can_create_a_buffer(self):
        buffer = UndoableBuffer()

    def test_can_move_cursor_in_buffer(self):
        buffer = UndoableBuffer()
        buffer.place_cursor(buffer.get_end_iter())

    def test_can_create_an_editor(self):
        editor = BasicEdit(PyroomConfig())

