import sys
sys.path.append('../PyRoom')

import unittest

# mock out gettext
import __builtin__
__builtin__._ = lambda str: str

from basic_edit import BasicEdit
from preferences import PyroomConfig
from basic_edit import Session


class SessionAcceptanceTest(unittest.TestCase):

    test_filename = 'some/test/file.txt'

    def test_testing_framework_is_setup(self):
        self.assertEqual(True, True)

    def test_assert_opened_file_is_added_to_session(self):
        pyroom_config = PyroomConfig()
        base_edit = BasicEdit(pyroom_config)
        
        base_edit.open_file_no_chooser(self.test_filename)

        session_filenames = base_edit.session.get_open_filenames()
        self.assertTrue(self.test_filename in session_filenames)

    def test_assert_opened_then_closed_file_is_not_in_session(self):
        pyroom_config = PyroomConfig()
        base_edit = BasicEdit(pyroom_config)

        base_edit.open_file_no_chooser(self.test_filename)
        base_edit.close_buffer()

        session_filenames = base_edit.session.get_open_filenames()
        self.assertTrue(self.test_filename not in session_filenames)

    # def test_session_is_persisted_outside_editor(self):
    #     pyroom_config = PyroomConfig()
    #     base_edit = BasicEdit(pyroom_config)

    #     base_edit.open_file_no_chooser(self.test_filename)
    #     del base_edit

    #     base_edit = BasicEdit(pyroom_config)
    #     session_filenames = base_edit.session.get_open_filenames()
    #     self.assertTrue(self.test_filename in session_filenames)
        
    def test_shelf_is_created(self):
        session = Session()
        self.assertEquals([], session.shelf['open_filenames'])

    def test_shelf_can_add_and_initialize_is_fine(self):
        session = Session()
        session.add_open_filename('test/filename.txt')
        self.assertTrue('test/filename.txt' in session.shelf.get('open_filenames'))




    
        
