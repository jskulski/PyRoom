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

    def test_create_an_editor_object(self):
        pyroom_config = PyroomConfig()
        base_edit = BasicEdit(pyroom_config)
        base_edit.open_file_no_chooser('some/test/file.txt')
        session_filenames = base_edit.session.get_open_filenames()
        self.assertTrue('some/test/file.txt' in session_filenames)
