import sys
sys.path.append('../PyRoom')

import gettext

import unittest

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
