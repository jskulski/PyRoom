from unittest import TestCase

import sys
sys.path.append('../PyRoom')

# mock out gettext
import __builtin__
__builtin__._ = lambda str: str

import os
import editor_input
from spy import spy

from PyRoom import autosave

from PyRoom.factory import Factory
from PyRoom.preferences import PyroomConfig
from PyRoom.editor import BasicEdit


class TestAutosaveAcceptance(TestCase):

    def setUp(self):
        self.autosave_time = 20

        self.pyroom_config = PyroomConfig()
        self.pyroom_config.set('editor', 'autosave', '1')
        self.pyroom_config.set('editor', 'autosavetime', str(self.autosave_time))
        self.pyroom_config.set('session', 'private', '1')

        self.factory = Factory()
        self.editor = self.factory.create_new_editor(self.pyroom_config)

    def tearDown(self):
        autosave.stop_autosave(self.editor)

    def test_when_an_editor_is_created_my_file_is_saved_after_configurable_time(self):

        expected_content = 'hello these are words in a document'
        editor_input.type_keys(expected_content, self.editor)
        self.editor.get_current_buffer().filename = 'a-file-im-working-on'
        expected_autosave_filepath = autosave.get_autosave_filename(
            self.editor.get_current_buffer().filename
        )

        self._trick_editor_into_thinking_time_has_passed(self.editor, self.autosave_time)
        autosave.autosave_timeout(self.editor)

        self.assertTrue(os.path.isfile(expected_autosave_filepath))
        with open(expected_autosave_filepath) as autosave_file:
            autosave_contents = autosave_file.read()
        self.assertEquals(autosave_contents, expected_content)


    def test_gui_is_asked_to_show_restore_autosave_dialog(self):
        filepath = self._generate_temporary_filepath()
        autosave_filepath = autosave.get_autosave_filename(filepath)
        autosave_file = open(autosave_filepath, 'w')
        autosave_file.write('this is the contents of a file')
        autosave_file.close()
        self.editor.gui.user_wants_to_restore_backup = spy()

        self.editor.open_file(filepath)

        self.assertTrue(self.editor.gui.user_wants_to_restore_backup.was_called)

    def _trick_editor_into_thinking_time_has_passed(self, editor, autosave_time):
        enough_elapsed_time_counter = 60 * autosave_time
        editor.autosave_elapsed = enough_elapsed_time_counter

    def _generate_temporary_filepath(self):
        import tempfile
        temporary_filename = next(tempfile._get_candidate_names())
        return os.path.join(tempfile.gettempdir(), temporary_filename)
