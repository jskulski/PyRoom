import sys
sys.path.append('../PyRoom')

import unittest

# mock out gettext
import __builtin__
__builtin__._ = lambda str: str

from basic_edit import BasicEdit
from preferences import PyroomConfigFileBuilderAndReader
from PyRoom.preferences import PyroomConfig

from basic_edit import Session

class SessionAcceptanceTest(unittest.TestCase):

    test_filename = 'some/test/file.txt'

    def setUp(self):
        self.pyroom_config_file_builder_and_reader = PyroomConfigFileBuilderAndReader()
        self.pyroom_config_file_builder_and_reader.config.clear_session = 1
        self.base_edit = BasicEdit(self.pyroom_config_file_builder_and_reader.config)

    def test_testing_framework_is_setup(self):
        self.assertEqual(True, True)

    def test_assert_opened_file_is_added_to_session(self):
        self.base_edit.open_file_and_add_to_session(self.test_filename)

        session_filenames = self.base_edit.session.get_open_filenames()
        self.assertTrue(self.test_filename in session_filenames)

    def test_assert_opened_then_closed_file_is_not_in_session(self):
        self.base_edit.open_file_and_add_to_session(self.test_filename)
        self.base_edit.close_buffer()

        session_filenames = self.base_edit.session.get_open_filenames()
        self.assertTrue(self.test_filename not in session_filenames)

    def test_session_is_persisted_outside_editor(self):
        self.base_edit.open_file_and_add_to_session(self.test_filename)
        del self.base_edit

        pyroom_config = PyroomConfigFileBuilderAndReader()
        restarted_base_edit = BasicEdit(pyroom_config.config)
        session_filenames = restarted_base_edit.session.get_open_filenames()
        self.assertTrue(self.test_filename in session_filenames)

    def test_editor_can_be_started_with_clean_session(self):
        self.base_edit.open_file_and_add_to_session(self.test_filename)
        del self.base_edit

        pyroom_config = PyroomConfigFileBuilderAndReader()
        pyroom_config.config.clear_session = True
        restarted_base_edit = BasicEdit(pyroom_config.config)

        session_filenames = restarted_base_edit.session.get_open_filenames()
        self.assertEquals([], session_filenames)

    def test_editor_can_have_a_private_session(self):
        pyroom_config = PyroomConfig()
        pyroom_config.set('session', 'private', '1')
        editor = BasicEdit(pyroom_config)

    def test_buffers_are_opened_for_files_in_session(self):
        self.base_edit.open_file_and_add_to_session(self.test_filename)
        del self.base_edit

        pyroom_config = PyroomConfigFileBuilderAndReader()
        restarted_base_edit = BasicEdit(pyroom_config.config)

        buffer_filenames = [buffer.filename for buffer in restarted_base_edit.buffers]
        self.assertTrue(self.test_filename in buffer_filenames)

    def test_opening_buffers_during_init_does_not_readd_to_session(self):
        """ Opening buffers during init from the session shouldn't """
        """ readd them to the session, duplicating the history """
        self.base_edit.open_file(self.test_filename)
        del self.base_edit

        pyroom_config = PyroomConfigFileBuilderAndReader()
        restarted_base_edit = BasicEdit(pyroom_config.config)

        session_filenames = restarted_base_edit.session.get_open_filenames()
        self.assertEquals([self.test_filename], session_filenames)

    def test_shelf_is_created(self):
        session = Session()
        session.clear()
        self.assertEquals([], session.shelf['open_filenames'])

    def test_shelf_can_add_and_initialize_is_fine(self):
        session = Session()
        session.add_open_filename('test/filename.txt')
        self.assertTrue(
            'test/filename.txt' in session.shelf.get('open_filenames')
        )

    def test_we_can_start_with_a_clean_session(self):
        session = Session()
        session.add_open_filename('test/filename.txt')
        session.clear()
        self.assertTrue(
            'test/filename.txt' not in session.get_open_filenames()
        )
