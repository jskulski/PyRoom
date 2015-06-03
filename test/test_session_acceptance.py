import os
import sys
sys.path.append('../PyRoom')

import unittest
import tempfile

# mock out gettext
import __builtin__
__builtin__._ = lambda str: str

import editor_input
from basic_edit import BasicEdit
from preferences import PyroomConfigFileBuilderAndReader
from PyRoom.preferences import PyroomConfig

from PyRoom.basic_edit import FileStoreSession

class SessionAcceptanceTest(unittest.TestCase):

    test_filename = 'some/test/file.txt'
    session_filepath = '/tmp/pyroom.unittest.session'

    def setUp(self):
        self._clear_session_file()

        self.pyroom_config = PyroomConfig()
        self.pyroom_config.clear_session = 1
        self.base_edit = BasicEdit(self.pyroom_config)

    def _clear_session_file(self):
        if (os.path.isfile(self.session_filepath)):
            os.remove(self.session_filepath)

    def test_we_can_tell_the_editor_where_to_store_the_session(self):

        session_filepath = '/tmp/pyroom.unittest.unique.session'

        if (os.path.isfile(session_filepath)):
            os.remove(session_filepath)
        pyroom_config = PyroomConfig()
        pyroom_config.set('session', 'filepath', session_filepath)

        editor = BasicEdit(pyroom_config)
        test_file = tempfile.NamedTemporaryFile()
        test_filepath = test_file.name
        test_file.write('this is the test contents oohh wee ooooo')
        editor.open_file_and_add_to_session(test_filepath)


        self.assertTrue(os.path.isfile(session_filepath))

        file_store_sesion = FileStoreSession(session_filepath)
        self.assertEquals(
            [test_filepath],
            file_store_sesion.get_open_filenames()
        )

        os.remove(session_filepath)

    def test_saving_a_file_will_add_file_to_session(self):
        session_filepath = tempfile.NamedTemporaryFile().name
        saved_filepath = '/tmp/pyroom.session.testfile'

        if (os.path.isfile(saved_filepath)):
            os.remove(saved_filepath)
        if (os.path.isfile(session_filepath)):
            os.remove(session_filepath)

        pyroom_config = PyroomConfig()
        pyroom_config.set('session', 'filepath', session_filepath)
        editor = BasicEdit(pyroom_config)

        editor_input.type_keys('Hello, how are you to day?', editor)
        editor.get_current_buffer().filename = saved_filepath
        editor.save_file_to_disk_and_session()
        del editor

        editor_restarted = BasicEdit(pyroom_config)

        self.assertEquals(
            editor_restarted.get_current_buffer().filename,
            saved_filepath
        )








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

        pyroom_config = PyroomConfig()
        restarted_base_edit = BasicEdit(pyroom_config)
        session_filenames = restarted_base_edit.session.get_open_filenames()
        self.assertTrue(self.test_filename in session_filenames)

    def test_editor_can_be_started_with_clean_session(self):
        self.base_edit.open_file_and_add_to_session(self.test_filename)
        del self.base_edit

        pyroom_config = PyroomConfig()
        pyroom_config.clear_session = True
        restarted_base_edit = BasicEdit(pyroom_config)

        session_filenames = restarted_base_edit.session.get_open_filenames()
        self.assertEquals([], session_filenames)

    def test_buffers_are_opened_for_files_in_session(self):
        self.base_edit.open_file_and_add_to_session(self.test_filename)
        del self.base_edit

        pyroom_config = PyroomConfig()
        restarted_base_edit = BasicEdit(pyroom_config)

        buffer_filenames = [buffer.filename for buffer in restarted_base_edit.buffers]
        self.assertTrue(self.test_filename in buffer_filenames)

    def test_opening_buffers_during_init_does_not_readd_to_session(self):
        """ Opening buffers during init from the session shouldn't
            readd them to the session, duplicating history """
        self.base_edit.open_file(self.test_filename)
        del self.base_edit

        pyroom_config = PyroomConfig()
        restarted_base_edit = BasicEdit(pyroom_config)

        session_filenames = restarted_base_edit.session.get_open_filenames()
        self.assertEquals([self.test_filename], session_filenames)

    def test_shelf_is_created(self):
        session = FileStoreSession(self.session_filepath)
        session.clear()
        self.assertEquals([], session.shelf['open_filenames'])

    def test_shelf_can_add_and_initialize_is_fine(self):
        session = FileStoreSession(self.session_filepath)
        session.add_open_filename('test/filename.txt')
        self.assertTrue(
            'test/filename.txt' in session.shelf.get('open_filenames')
        )

    def test_we_can_start_with_a_clean_session(self):
        session = FileStoreSession(self.session_filepath)
        session.add_open_filename('test/filename.txt')
        session.clear()
        self.assertTrue(
            'test/filename.txt' not in session.get_open_filenames()
        )
