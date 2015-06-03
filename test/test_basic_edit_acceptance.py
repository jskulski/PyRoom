from unittest import TestCase

import sys
sys.path.append('../PyRoom')

# mock out gettext
import __builtin__
__builtin__._ = lambda str: str


import editor_input
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

    def test_can_type_in_editor_and_see_it_in_buffer(self):
        pyroom_config = PyroomConfig()
        editor = BasicEdit(pyroom_config)

        hello_world = "Hello, World!"
        editor_input.type_key(hello_world)
        self.assertEquals(
            hello_world,
            editor_input.retrieve_current_buffer_text(editor)
        )

    def test_can_open_file_in_editor(self):
        test_file_path = 'test_file.txt'
        with file(test_file_path) as test_file:
            test_file_contents = test_file.read()

        pyroom_config = PyroomConfig()
        pyroom_config.clear_session = 1
        editor = BasicEdit(pyroom_config)
        editor.open_file(test_file_path)

        self.assertEquals(
            test_file_contents,
            editor_input.retrieve_current_buffer_text(editor)
        )
