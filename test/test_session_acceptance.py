import sys
sys.path.append('../PyRoom')

import unittest

# mock out gettext
import __builtin__
__builtin__._ = lambda str: str

from basic_edit import BasicEdit
from preferences import PyroomConfig


class SessionAcceptanceTest(unittest.TestCase):

    def test_testing_framework_is_setup(self):
        self.assertEqual(True, True)

    def test_assert_opened_file_is_added_to_session(self):
        pyroom_config = PyroomConfig()
        base_edit = BasicEdit(pyroom_config)

        base_edit.open_file_no_chooser('some/test/file.txt')

        session_filenames = base_edit.session.get_open_filenames()
        self.assertTrue('some/test/file.txt' in session_filenames)

    def test_assert_opened_then_closed_file_is_not_in_session(self):
        pyroom_config = PyroomConfig()
        base_edit = BasicEdit(pyroom_config)

        base_edit.open_file_no_chooser('some/test/file.txt')
        base_edit.close_buffer()

        session_filenames = base_edit.session.get_open_filenames()
        self.assertTrue('some/test/file.txt' not in session_filenames)


