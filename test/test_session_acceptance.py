import os
import sys
sys.path.append('../PyRoom')

import unittest
import tempfile

# mock out gettext
import __builtin__
__builtin__._ = lambda str: str

import editor_input

from PyRoom.factory import Factory
from PyRoom.preferences import PyroomConfig

from PyRoom.editor import FileStoreSession

class SessionAcceptanceTest(unittest.TestCase):


    def setUp(self):
        self.factory = Factory()
        self.session_filepath = self._generate_temporary_filepath()
        self.test_filepath = self._generate_temporary_filepath()

        self.pyroom_config = PyroomConfig()
        self.pyroom_config.set('session', 'filepath', self.session_filepath)
        self.editor = self.factory.create_new_editor(self.pyroom_config)

    def tearDown(self):
        if (os.path.isfile(self.session_filepath)):
            os.remove(self.session_filepath)

        if (os.path.isfile(self.test_filepath)):
            os.remove(self.test_filepath)

    def test_we_can_tell_the_editor_where_to_store_the_session(self):
        test_filepath = self._edit_test_file_and_save(self.editor)

        file_store_session = FileStoreSession(self.session_filepath)
        self.assertEquals(
            [test_filepath],
            file_store_session.get_open_filenames()
        )

        os.remove(self.session_filepath)

    def test_saving_a_file_will_add_file_to_session(self):
        saved_filepath = '/tmp/pyroom.session.testfile'

        if (os.path.isfile(saved_filepath)):
            os.remove(saved_filepath)

        editor = self.editor

        editor_input.type_keys('Hello, how are you to day?', editor)
        editor.get_current_buffer().filename = saved_filepath
        editor.save_file_to_disk_and_session(),
        del editor

        editor_restarted = self.factory.create_new_editor(self.pyroom_config)

        self.assertEquals(
            saved_filepath,
            editor_restarted.get_current_buffer().filename
        )

    def test_assert_opened_file_is_added_to_session(self):
        self.editor.open_file_and_add_to_session(self.test_filepath)

        session_filenames = self.editor.session.get_open_filenames()

        self.assertTrue(self.test_filepath in session_filenames)

    def test_assert_opened_then_closed_file_is_not_in_session(self):
        self.editor.open_file_and_add_to_session(self.test_filepath)
        self.editor.close_current_buffer()

        session_filenames = self.editor.session.get_open_filenames()
        self.assertTrue(self.test_filepath not in session_filenames)

    def test_session_is_persisted_outside_editor(self):
        self.editor.open_file_and_add_to_session(self.test_filepath)
        del self.editor

        restarted_editor = self.factory.create_new_editor(self.pyroom_config)
        session_filenames = restarted_editor.session.get_open_filenames()
        self.assertTrue(self.test_filepath in session_filenames)

    def test_editor_can_be_started_with_clean_session(self):
        self.editor.open_file_and_add_to_session(self.test_filepath)
        del self.editor

        self.pyroom_config.clear_session = True
        restarted_editor = self.factory.create_new_editor(self.pyroom_config)

        session_filenames = restarted_editor.session.get_open_filenames()
        self.assertEquals([], session_filenames)

    def test_buffers_are_opened_for_files_in_session(self):
        self.editor.open_file_and_add_to_session(self.test_filepath)
        del self.editor

        restarted_editor = self.factory.create_new_editor(self.pyroom_config)

        buffer_filenames = [buffer.filename for buffer in restarted_editor.buffers]
        self.assertTrue(self.test_filepath in buffer_filenames)

    def test_opening_buffers_during_init_does_not_readd_to_session(self):
        self.editor.open_file_and_add_to_session(self.test_filepath)
        del self.editor

        restarted_editor = self.factory.create_new_editor(self.pyroom_config)

        session_filenames = restarted_editor.session.get_open_filenames()
        self.assertEquals([self.test_filepath], session_filenames)

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

    def test_private_session_has_one_unnamed_buffer_and_empty(self):
        editor = self._create_private_session_editor(self.session_filepath)

        self.assertEquals(len(editor.session.get_open_filenames()), 0)
        self.assertEquals(len(editor.buffers), 1)
        self.assertTrue(editor.get_current_buffer().has_no_filename())

    def test_private_session_does_not_open_file_store_session(self):
        user_session_editor = self._create_user_session_editor(self.session_filepath)
        self._edit_test_file_and_save(user_session_editor)

        private_session_editor = self._create_private_session_editor(self.session_filepath)

        self.assertEquals(len(private_session_editor.session.get_open_filenames()), 0)
        self.assertEquals(len(private_session_editor.buffers), 1)
        self.assertTrue(private_session_editor.get_current_buffer().has_no_filename())

    def _edit_test_file_and_save(self, editor):
        test_file = tempfile.NamedTemporaryFile()
        test_filepath = test_file.name
        test_file.write('this is the test contents oohh wee ooooo')
        editor.open_file_and_add_to_session(test_filepath)
        return test_filepath

    def _create_user_session_editor(self, session_filepath):
        user_session_pyroom_config = PyroomConfig()
        user_session_pyroom_config.set('session', 'private', '0')
        user_session_pyroom_config.set('session', 'filepath', session_filepath)
        return self.factory.create_new_editor(user_session_pyroom_config)

    def _create_private_session_editor(self, session_filepath):
        private_session_pyroom_config = PyroomConfig()
        private_session_pyroom_config.set('session', 'private', '1')
        private_session_pyroom_config.set('session', 'filepath', session_filepath)
        return self.factory.create_new_editor(private_session_pyroom_config)

    def _generate_temporary_filepath(self):
        temporary_filename = next(tempfile._get_candidate_names())
        return os.path.join(tempfile.gettempdir(), temporary_filename)
