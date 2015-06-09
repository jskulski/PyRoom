from unittest import TestCase

import sys
sys.path.append('../PyRoom')

# mock out gettext
import __builtin__
__builtin__._ = lambda str: str


import editor_input
from PyRoom.gui import AbstractGUI
from PyRoom.preferences import PyroomConfig
from PyRoom.basic_edit import BasicEdit
from PyRoom.undoable_buffer import UndoableBuffer


def test_can_create_an_editor_with_mock_gui(self):
    pyroom_config = PyroomConfig()
    pyroom_config.set('session', 'private', '1')
    editor = BasicEdit(pyroom_config, I())
    pass


class MockGUI(AbstractGUI):
    def apply_theme(self):
        super(MockGUI, self).apply_theme()

    def scroll_event(self, widget, event):
        super(MockGUI, self).scroll_event(widget, event)

    def destroy(self, widget, data):
        super(MockGUI, self).destroy(widget, data)

    def quit(self):
        super(MockGUI, self).quit()

    def scroll_down(self):
        super(MockGUI, self).scroll_down()

    def scroll_up(self):
        super(MockGUI, self).scroll_up()

