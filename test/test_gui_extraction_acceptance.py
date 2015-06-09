from unittest import TestCase

import sys
sys.path.append('../PyRoom')

# mock out gettext
import __builtin__
__builtin__._ = lambda str: str


import editor_input
from PyRoom.gui import AbstractGUI
from PyRoom.gui import GUI
from PyRoom.preferences import PyroomConfig
from PyRoom.basic_edit import BasicEdit
from PyRoom.undoable_buffer import UndoableBuffer


class GUIExtractionAcceptanceTest(TestCase):

    mock_buffers = [
        UndoableBuffer(),
        UndoableBuffer(),
        UndoableBuffer(),
    ]

    def setUp(self):
        self.pyroom_config = PyroomConfig()
        self.pyroom_config.set('session', 'private', '1')
        self.editor = BasicEdit(self.pyroom_config)

    def test_can_supercede_gui_in_editor(self):
        gui = MockGUI()
        self.editor.gui = gui

    def test_setting_buffer_tells_gtk_textbox_to_set_buffer(self):
        def test_set_buffer_is_called(text_buffer):
            self.assertEquals(
                text_buffer,
                self.mock_buffers[2].text_buffer
            )

        gui = GUI(self.pyroom_config)
        gui.textbox.set_buffer = test_set_buffer_is_called
        self.editor.gui = gui

        self.editor.buffers = self.mock_buffers
        self.editor.set_buffer(2)

    def test_switching_to_next_buffer_sets_the_expected_buffer(self):
        class WasCalled:
            called = False
        def _test_scroll_to_mark_called(buffer_insert, position):
            WasCalled.called = True
            self.assertEquals(
                buffer_insert,
                self.mock_buffers[1].get_insert()
            )
            self.assertEquals(0.0, position)

        self.editor.buffers = self.mock_buffers

        gui = GUI(self.pyroom_config)
        gui.textbox.scroll_to_mark = _test_scroll_to_mark_called
        self.editor.supercede_gui(gui)

        self.editor.next_buffer()
        self.assertTrue(WasCalled.called)

class MockGUI(AbstractGUI):

    def __init__(self):
        pass

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

