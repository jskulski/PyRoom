import unittest

import sys
sys.path.append('../PyRoom')

# mock out gettext
import __builtin__
__builtin__._ = lambda str: str


import editor_input
from PyRoom.preferences import PyroomConfig
from PyRoom.basic_edit import BasicEdit
from PyRoom.undoable_buffer import UndoableBuffer

class TestAutosaveAcceptance(unittest.TestCase):

    def test_can_create_editor_with_autosave(self):
        pyroom_config = PyroomConfig()
        pyroom_config.set('editor', 'autosave', '1')
        # editor = BasicEdit(pyroom_config)


