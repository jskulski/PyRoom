from unittest import TestCase

import sys
sys.path.append('../PyRoom')

# mock out gettext
import __builtin__
__builtin__._ = lambda str: str

import os


from PyRoom.preferences import PyroomConfig
from PyRoom.basic_edit import BasicEdit

import autosave


class TestAutosaveAcceptance(TestCase):

    def test_when_an_editor_is_created_my_file_is_saved_after_configurable_time(self):
        autosave_time = 20
        pyroom_config = PyroomConfig()
        pyroom_config.set('editor', 'autosave', '1')
        pyroom_config.set('editor', 'autosavetime', str(autosave_time))
        editor = BasicEdit(pyroom_config)

        expected_words = 'hello these are words'
        expected_autosave_filepath = autosave.get_autosave_filename()
        editor_input.type_keys(expected_words, editor)

        self.trick_editor_into_thinking_time_has_passed(editor, autosave_time)

        print expected_autosave_filepath
        self.assertTrue(os.path.isfile(expected_autosave_filepath))


    def trick_editor_into_thinking_time_has_passed(self, editor, autosave_time):
        enough_elapsed_time_counter = 60 * autosave_time
        editor.autosave_elapsed = enough_elapsed_time_counter


