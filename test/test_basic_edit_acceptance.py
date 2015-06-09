from unittest import TestCase

import sys
sys.path.append('../PyRoom')

# mock out gettext
import __builtin__
__builtin__._ = lambda str: str


import editor_input
from PyRoom.gui import NullGUI
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
        editor = self._create_private_session_editor()

        hello_world = "Hello, World"
        editor_input.type_keys(hello_world, editor)
        self.assertEquals(
            hello_world,
            editor_input.retrieve_current_buffer_text(editor)
        )

    def test_can_open_file_in_editor(self):
        test_file_path = 'test_file.txt'
        with file(test_file_path) as test_file:
            test_file_contents = test_file.read()

        editor = self._create_private_session_editor()
        editor.open_file(test_file_path)

        self.assertEquals(
            test_file_contents,
            editor_input.retrieve_current_buffer_text(editor)
        )

    def test_can_save_file_in_editor(self):
        test_file_path = '/tmp/pyroom.unittest.test_file'
        expected_test_file_contents = "Hello, this is my new file"

        editor = self._create_private_session_editor()

        editor_input.type_keys(expected_test_file_contents, editor)
        buffer = editor.get_current_buffer()
        test_file_path = '/tmp/pyroom.unittest.test_file'
        buffer.filename = test_file_path
        editor.save_file_to_disk()

        with open(test_file_path) as test_file:
            actual_test_file_contents = test_file.read()

        self.assertEquals(
            expected_test_file_contents,
            actual_test_file_contents
        )

    def _create_private_session_editor(self):
        pyroom_config = PyroomConfig()
        pyroom_config.set('session', 'private', '1')
        return BasicEdit(pyroom_config)

    def test_first_opened_buffer_is_unnamed(self):
        editor = self._create_private_session_editor()
        self.assertFalse(editor.get_current_buffer().has_filename())


    def test_can_create_an_editor_with_a_null_gui(self):
        #editor = BasicEdit(PyroomConfig(), NullGUI())
        pass
