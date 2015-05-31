import unittest

import sys
sys.path.append('../PyRoom')

# mock out gettext
import __builtin__
__builtin__._ = lambda str: str

from PyRoom.basic_edit import BasicEdit
from PyRoom.basic_edit import VimEmulator
from PyRoom.preferences import PyroomConfigFileBuilderAndReader

class VimEmulatorUnitTest(unittest.TestCase):

    def test_that_vim_emulator_is_in_command_mode_by_default(self):
        vim_emulator = VimEmulator()
        self.assertTrue(vim_emulator.in_command_mode())
        self.assertFalse(vim_emulator.in_insert_mode())

    def test_that_vim_emulator_can_toggle_mode(self):
        vim_emulator = VimEmulator()
        vim_emulator.toggle_mode()
        self.assertFalse(vim_emulator.in_command_mode())
        self.assertTrue(vim_emulator.in_insert_mode())

