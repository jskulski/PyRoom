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

    def setUp(self):
        self.pyroom_config = PyroomConfig()
        self.pyroom_config.set('session', 'private', '1')

        self.editor = BasicEdit(self.pyroom_config)
        self.mock_buffers = self._setup_mock_buffers()
        self.editor.buffers = self.mock_buffers

        self.gui = GUI(self.pyroom_config)
        self.editor.gui = self.gui
        self.disable_gtk_quit()

        self.spy_was_called = False

    def _setup_mock_buffers(self):
        return [
            UndoableBuffer(),
            UndoableBuffer(),
            UndoableBuffer(),
        ]


    def disable_gtk_quit(self):
        self.editor.gui.quit = self._noop

    def test_can_supercede_gui_in_editor(self):
        gui = MockGUI()
        self.editor.gui = gui

    def test_setting_buffer_tells_gtk_textbox_to_set_buffer(self):
        def test_set_buffer_is_called(text_buffer):
            self.assertEquals(
                text_buffer,
                self.mock_buffers[1].text_buffer
            )

        self.gui.textbox.set_buffer = test_set_buffer_is_called

        self.editor.set_buffer(1)

    def test_switching_to_next_buffer_sets_the_expected_buffer(self):
        self.editor.set_buffer(0)
        self.gui.textbox.scroll_to_mark = self._assert_cursor_scrolled_to_mark_to_middle_buffer

        self.editor.next_buffer()

        self.assertTrue(self.spy_was_called)

    def test_switching_to_prev_buffer_sets_expected_buffer(self):
        self.editor.set_buffer(2)
        self.gui.textbox.scroll_to_mark = self._assert_cursor_scrolled_to_mark_to_middle_buffer

        self.editor.prev_buffer()

        self.assertTrue(self.spy_was_called)

    def test_that_editing_a_buffer_then_quitting_causes_save_dialog(self):
        self.editor.set_buffer(0)
        def mock_quit_dialog():
            mock_quit_dialog.was_called = True
        mock_quit_dialog.was_called = False
        self.editor.quitdialog.show = mock_quit_dialog
        editor_input.type_keys('modify the buffer', self.editor)

        self.editor.ask_to_save_if_modifed_buffers_else_quit()

        self.assertTrue(self.editor.quitdialog.show.was_called)

    def test_that_quitting_with_no_modified_buffers_does_not_show_dialog(self):
        self.editor.set_buffer(0)
        def mock_quit_dialog():
            mock_quit_dialog.was_called = True
        mock_quit_dialog.was_called = False
        self.editor.quitdialog.show = mock_quit_dialog

        self.editor.ask_to_save_if_modifed_buffers_else_quit()

        self.assertFalse(self.editor.quitdialog.show.was_called)


    def _noop(self):
        pass

    def _assert_cursor_scrolled_to_mark_to_middle_buffer(self, buffer_insert, position):
        self.spy_was_called = True

        self.assertEquals(
            buffer_insert,
            self.mock_buffers[1].get_insert()
        )
        self.assertEquals(0.0, position)




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

