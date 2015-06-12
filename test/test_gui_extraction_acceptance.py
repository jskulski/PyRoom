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

        self.editor.gui.textbox.set_buffer = test_set_buffer_is_called

        self.editor.set_buffer(1)

    def test_switching_to_next_buffer_sets_the_expected_buffer(self):
        self.editor.set_buffer(0)
        self.editor.gui.textbox.scroll_to_mark = self._assert_cursor_scrolled_to_mark_to_middle_buffer

        self.editor.next_buffer()

        self.assertTrue(self.spy_was_called)

    def test_switching_to_prev_buffer_sets_expected_buffer(self):
        self.editor.set_buffer(2)
        self.editor.gui.textbox.scroll_to_mark = self._assert_cursor_scrolled_to_mark_to_middle_buffer

        self.editor.prev_buffer()

        self.assertTrue(self.spy_was_called)

    def test_that_editing_a_buffer_then_quitting_causes_save_dialog(self):
        self.editor.set_buffer(0)
        self.editor.gui.quitdialog.show = self.spy()
        editor_input.type_keys('modify the buffer', self.editor)

        self.editor.save_dialog_or_quit_editor()

        self.assertTrue(self.editor.gui.quitdialog.show.was_called)

    def test_that_quitting_with_no_modified_buffers_does_not_show_dialog(self):
        self.editor.set_buffer(0)
        self.editor.gui.quitdialog.show = self.spy()

        self.editor.save_dialog_or_quit_editor()

        self.assertFalse(self.editor.gui.quitdialog.show.was_called)

    def test_close_action_on_quit_dialog_hides_dialog(self):
        self.editor.gui.quitdialog.hide = self.spy()
        self.editor.quit = self.spy()

        editor_input.type_keys('modifying the buffer with strings', self.editor)
        self.editor.close_button_handler(None)

        self.assertTrue(self.editor.gui.quitdialog.hide.was_called)
        self.assertTrue(self.editor.quit.was_called)

    def test_cancel_action_hides_dialog_and_does_not_quit(self):
        self.editor.gui.quitdialog.hide = self.spy()
        self.editor.quit = self.spy()

        editor_input.type_keys('modifying the buffer with strings', self.editor)
        self.editor.cancel_quit(None)

        self.assertTrue(self.editor.gui.quitdialog.hide.was_called)
        self.assertFalse(self.editor.quit.was_called)

    def test_save_action_hides_dialog_saves_buffer_and_quits(self):
        self.editor.set_buffer(0)
        self.editor.gui.quitdialog.hide = self.spy()
        self.editor.quit = self.spy()
        self.editor.ask_for_filename_and_save_buffer = self.spy()

        editor_input.type_keys('modifying buffer with strings', self.editor)
        self.editor.save_quit(None)

        self.assertTrue(self.editor.gui.quitdialog.hide.was_called)
        self.assertTrue(self.editor.ask_for_filename_and_save_buffer.was_called)
        self.assertTrue(self.editor.quit.was_called)

    def test_closing_buffer_on_modified_buffer_shows_dialog(self):
        self.editor.set_buffer(0)
        editor_input.type_keys('modifying buffer with strings', self.editor)
        self.editor.closedialog.show = self.spy()

        self.editor.close_dialog()

        self.assertTrue(self.editor.closedialog.show.was_called)

    def test_cancel_on_close_dialog_hides_dialog_does_not_close_buffer(self):
        self.editor.set_buffer(0)
        editor_input.type_keys('modifying buffer with strings', self.editor)
        self.editor.closedialog.hide = self.spy()
        expected_current_buffer = self.editor.get_current_buffer()

        self.editor.cancel_dialog(None)

        self.assertTrue(self.editor.closedialog.hide.was_called)
        self.assertEquals(
            self.editor.get_current_buffer(),
            expected_current_buffer
        )

    def test_close_without_saving_button_hides_dialog_and_does_what_it_says(self):
        self.editor.set_buffer(0)
        editor_input.type_keys('modifying buffer with strings', self.editor)
        next_buffer_in_stack = self.editor.buffers[1]
        self.editor.closedialog.hide = self.spy()
        self.editor.save_file_to_disk = self.spy()

        self.editor.unsave_dialog(None)

        self.assertTrue(self.editor.closedialog.hide.was_called)
        self.assertEqual(
            self.editor.get_current_buffer(),
            next_buffer_in_stack
        )
        self.assertFalse(self.editor.save_file_to_disk.was_called)

    # def test_close_with_save_button_works_as_advertised(self):
    #     self.editor.set_buffer(0)
    #     editor_input.type_keys('modifying buffer with strings', self.editor)
    #     self.editor.closedialog.hide = self.spy()
    #     next_buffer_in_stack = self.editor.buffers[1]
    #
    #

    def spy(self):
        def mock_quit_dialog(*args, **kwargs):
            mock_quit_dialog.was_called = True

        mock_quit_dialog.was_called = False
        return mock_quit_dialog

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

