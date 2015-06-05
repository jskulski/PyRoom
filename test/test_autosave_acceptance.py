from unittest import TestCase

import sys
sys.path.append('../PyRoom')

# mock out gettext
import __builtin__
__builtin__._ = lambda str: str

import os

import editor_input

from PyRoom import autosave
from PyRoom.preferences import PyroomConfig
from PyRoom.basic_edit import BasicEdit


class TestAutosaveAcceptance(TestCase):

    def test_when_an_editor_is_created_my_file_is_saved_after_configurable_time(self):
        autosave_time = 20
        pyroom_config = PyroomConfig()
        pyroom_config.set('editor', 'autosave', '1')
        pyroom_config.set('editor', 'autosavetime', str(autosave_time))
        pyroom_config.clear_session = 1
        editor = BasicEdit(pyroom_config)

        expected_content = 'hello these are words in a document'
        editor_input.type_keys(expected_content, editor)
        editor.get_current_buffer().filename = 'a-file-im-working-on'
        expected_autosave_filepath = autosave.get_autosave_filename(
            editor.get_current_buffer().filename
        )

        self.trick_editor_into_thinking_time_has_passed(editor, autosave_time)
        autosave.autosave_timeout(editor)

        self.assertTrue(os.path.isfile(expected_autosave_filepath))
        with open(expected_autosave_filepath) as autosave_file:
            autosave_contents = autosave_file.read()
        self.assertEquals(autosave_contents, expected_content)

        autosave.stop_autosave(editor)

    def trick_editor_into_thinking_time_has_passed(self, editor, autosave_time):
        enough_elapsed_time_counter = 60 * autosave_time
        editor.autosave_elapsed = enough_elapsed_time_counter


