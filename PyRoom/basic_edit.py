# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# PyRoom - A clone of WriteRoom
# Copyright (c) 2007 Nicolas P. Rougier & NoWhereMan
# Copyright (c) 2008 The Pyroom Team - See AUTHORS file for more information
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------

"""
provide basic editor functionality

contains basic functions needed for pyroom - any core functionality is included
within this file
"""

import gtk
import gtk.glade
import os
import urllib

from pyroom_error import PyroomError
from gui import GUI
from preferences import Preferences

from session import FileStoreSession
from session import PrivateSession
from undoable_buffer import UndoableBuffer

import autosave

FILE_UNNAMED = _('* Unnamed *')

KEY_BINDINGS = '\n'.join([
_('Control-H: Show help in a new buffer'),
_('Control-I: Show buffer information'),
_('Control-P: Shows Preferences dialog'),
_('Control-N: Create a new buffer'),
_('Control-O: Open a file in a new buffer'),
_('Control-Q: Quit'),
_('Control-S: Save current buffer'),
_('Control-Shift-S: Save current buffer as'),
_('Control-W: Close buffer and exit if it was the last buffer'),
_('Control-Y: Redo last typing'),
_('Control-Z: Undo last typing'),
_('Control-Page Up: Switch to previous buffer'),
_('Control-Page Down: Switch to next buffer'), ])

HELP = \
    _("""PyRoom - distraction free writing
Copyright (c) 2007 Nicolas Rougier, NoWhereMan
Copyright (c) 2008 Bruno Bord and the PyRoom team

Welcome to PyRoom and distraction-free writing.

To hide this help window, press Control-W.

PyRoom stays out of your way with formatting options and buttons, 
it is largely keyboard controlled, via shortcuts. You can find a list
of available keyboard shortcuts later.

If enabled in preferences, pyroom will save your files automatically every
few minutes or when you press the keyboard shortcut.

Commands:
---------
%s

""") % KEY_BINDINGS


def dispatch(*args, **kwargs):
    """call the method passed as args[1] without passing other arguments"""
    def eat(accel_group, acceleratable, keyval, modifier):
        """eat all the extra arguments

        this is ugly, but it works with the code we already had
        before we changed to AccelGroup et al"""
        args[0]()
        pass
    return eat

    
def make_accel_group(edit_instance):
    keybindings = {
        'h': edit_instance.show_help,
        'i': edit_instance.show_info,
        'n': edit_instance.new_buffer,
        'o': edit_instance.open_file_dialog,
        'p': edit_instance.preferences.show,
        'q': edit_instance.save_dialog_or_quit_editor,
        's': edit_instance.save_file_to_disk_and_session,
        'w': edit_instance.close_dialog,
        'y': edit_instance.redo,
        'z': edit_instance.undo,
    }
    ag = gtk.AccelGroup()
    for key, value in keybindings.items():
        ag.connect_group(
            ord(key),
            gtk.gdk.CONTROL_MASK,
            gtk.ACCEL_VISIBLE,
            dispatch(value)
        )
    ag.connect_group(
        ord('s'),
        gtk.gdk.CONTROL_MASK|gtk.gdk.SHIFT_MASK,
        gtk.ACCEL_VISIBLE,
        dispatch(edit_instance.save_file_as)
    )
    return ag

def define_keybindings(edit_instance):
    """define keybindings, respectively to keyboard layout"""
    keymap = gtk.gdk.keymap_get_default()
    testter = {
        gtk.keysyms.Page_Up: edit_instance.prev_buffer,
        gtk.keysyms.Page_Down: edit_instance.next_buffer,
    }
    translated_bindings = {}
    for key, value in testter.items():
        hardware_keycode = keymap.get_entries_for_keyval(key)[0][0]
        translated_bindings[hardware_keycode] = value
    return translated_bindings


class BasicEdit(object):
    """editing logic that gets passed around
       also, handles interaction and creation of the GUI"""

    def __init__(self, pyroom_config, gui=None, preferences=None):
        self.current = 0
        self.buffers = []
        self.config = pyroom_config

        if gui is None:
            self.gui = GUI(self.config)
        else:
            self.gui = gui

        if (self.config.get('editor', 'vim_emulation_mode') == '1'):
            self.vim_emulator = VimEmulator()
        else:
            self.vim_emulator = None

        # Session Management
        if self.config.get('session', 'private') == '1':
            self.session = PrivateSession()
        else:
            self.session = FileStoreSession(self.config.get('session', 'filepath'))

        if self.config.clear_session:
            self.session.clear()


        if preferences is None:
            self.preferences = Preferences(
                gui=self.gui,
                pyroom_config=self.config
            )
        else:
            self.preferences = preferences

        try:
            self.recent_manager = gtk.recent_manager_get_default()
        except AttributeError:
            self.recent_manager = None
        self.status = self.gui.status
        self.window = self.gui.window
        self.gui.window.add_accel_group(make_accel_group(self))
        self.UNNAMED_FILENAME = FILE_UNNAMED

        self.autosave_timeout_id = ''
        self.autosave_elapsed = ''

        opened_file_list = self.session.get_open_filenames()
        for filename in opened_file_list:
            self.open_file(filename)

        if opened_file_list == []:
            self.new_buffer()

        self.gui.textbox.connect('key-press-event', self.key_press_event)

        self.gui.style_textbox()

        # Autosave timer object
        autosave.start_autosave(self)

        self.gui.window.show_all()
        self.gui.window.fullscreen()

        self._adjust_window_if_multiple_monitors()

        self.gui.create_close_buffer_dialog_and_register_handlers(
            self.close_buffer_save_button_handler,
            self.close_buffer_close_without_save_button_handler,
            self.close_buffer_cancel_button_handler
        )
        self.gui.create_quit_dialog_and_register_handlers(
            self.quit_dialog_save_button_handler,
            self.quit_dialog_close_button_handler,
            self.quit_dialog_cancel_button
        )

        self.keybindings = define_keybindings(self)
        # this sucks, shouldn't have to call this here, textbox should
        # have its background and padding color from GUI().__init__() already
        self.gui.apply_theme()

    def _adjust_window_if_multiple_monitors(self):
        screen = gtk.gdk.screen_get_default()
        root_window = screen.get_root_window()
        mouse_x, mouse_y, mouse_mods = root_window.get_pointer()
        current_monitor_number = screen.get_monitor_at_point(mouse_x, mouse_y)
        monitor_geometry = screen.get_monitor_geometry(current_monitor_number)
        self.gui.window.move(monitor_geometry.x, monitor_geometry.y)
        self.gui.window.set_geometry_hints(None, min_width=monitor_geometry.width,
                                       min_height=monitor_geometry.height, max_width=monitor_geometry.width,
                                       max_height=monitor_geometry.height
                                       )

    def key_press_event(self, widget, event):
        """ key press event dispatcher """
        if event.state & gtk.gdk.CONTROL_MASK:
            if event.hardware_keycode in self.keybindings:
                self.keybindings[event.hardware_keycode]()
                return True

        if self.vim_emulator and self.vim_emulator.in_command_mode() and event.keyval == gtk.keysyms.i:
            self.status.set_text('- Insert Mode -', 50)
            self.vim_emulator.toggle_mode()
            return True

        if self.vim_emulator and self.vim_emulator.in_insert_mode() and event.keyval == gtk.keysyms.Escape:
            self.status.set_text('- Command Mode -', 50)
            self.vim_emulator.toggle_mode()
            return True
        return False

    def show_info(self):
        """ Display buffer information on status label for 5 seconds """

        buf = self.get_current_buffer()
        if buf.modified:
            status = _(' (modified)')
        else:
            status = ''
        self.status.set_text(_('Buffer %(buffer_id)d: %(buffer_name)s\
%(status)s, %(char_count)d character(s), %(word_count)d word(s)\
, %(lines)d line(s)') % {
            'buffer_id': self.current + 1,
            'buffer_name': buf.filename,
            'status': status,
            'char_count': buf.get_char_count(),
            'word_count': self.word_count(buf),
            'lines': buf.get_line_count(),
            }, 5000)

    def undo(self):
        """ Undo last typing """

        buf = self.get_current_buffer()
        if buf.can_undo:
            buf.undo()
        else:
            self.status.set_text(_('Nothing more to undo!'))

    def redo(self):
        """ Redo last typing """

        buf = self.get_current_buffer()
        if buf.can_redo:
            buf.redo()
        else:
            self.status.set_text(_('Nothing more to redo!'))

    def ask_restore(self):
        """ask if backups should be restored

        returns True if proposal is accepted
        returns False in any other case (declined/dialog closed)"""
        restore_dialog = gtk.Dialog(
            title=_('Restore backup?'),
            parent=self.gui.window,
            flags=gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            buttons=(
                gtk.STOCK_DISCARD, gtk.RESPONSE_REJECT,
                gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT
            )
        )
        question_asked = gtk.Label(
            _('''Backup information for this file has been found.
Open those instead of the original file?''')
        )
        question_asked.set_line_wrap(True)

        question_sign = gtk.image_new_from_stock(
            stock_id=gtk.STOCK_DIALOG_QUESTION,
            size=gtk.ICON_SIZE_DIALOG
        )
        question_sign.show()

        hbox = gtk.HBox()
        hbox.pack_start(question_sign, True, True, 0)
        hbox.pack_start(question_asked, True, True, 0)
        hbox.show()
        restore_dialog.vbox.pack_start(
            hbox, True, True, 0
        )

        restore_dialog.set_default_response(gtk.RESPONSE_ACCEPT)
        restore_dialog.show_all()
        resp = restore_dialog.run()
        restore_dialog.destroy()
        return resp == -3

    def open_file_dialog(self):
        """ Open file """

        chooser = gtk.FileChooserDialog('PyRoom', self.gui.window,
                gtk.FILE_CHOOSER_ACTION_OPEN,
                buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        chooser.set_default_response(gtk.RESPONSE_OK)

        res = chooser.run()
        if res == gtk.RESPONSE_OK:
            self.open_file_and_add_to_session(chooser.get_filename())
        else:
            self.file_chooser_closed_with_no_file_selected()
        chooser.destroy()

    def open_file_and_add_to_session(self, filename):
        """ Open specified file in buffer and add it to our session history """
        self.session.add_open_filename(filename)
        self.open_file(filename)

    def open_file(self, filename):
        """ Open specified file """
        def check_backup(filename):
            """check if restore from backup is an option

            returns backup filename if there's a backup file and
                    user wants to restore from it, else original filename
            """
            fname = autosave.get_autosave_filename(filename)
            if os.path.isfile(fname):
                print '-------'
                print 'filename = %s ' % filename
                print 'autosave fname = %s ' % fname
                import traceback
                for line in traceback.format_stack():
                    print line.strip()
                print '-------'
                if self.ask_restore():
                    return fname
            return filename
        buf = self.new_buffer()
        buf.filename = filename
        filename_to_open = check_backup(filename)

        try:
            buffer_file = open(filename_to_open, 'r')
            buf = self.get_current_buffer()
            buf.begin_not_undoable_action()
            utf8 = unicode(buffer_file.read(), 'utf-8')
            buf.set_text(utf8)
            buf.end_not_undoable_action()
            buffer_file.close()


        except IOError, (errno, strerror):
            errortext = _('Unable to open %(filename)s.') % {
                'filename': filename_to_open
            }
            if errno == 13:
                errortext += _(' You do not have permission to open \
the file.')
            if not errno == 2:
                raise PyroomError(errortext)
        except:
            raise PyroomError(_('Unable to open %s\n') % filename_to_open)
        else:
            self.status.set_text(_('File %s open') % filename_to_open)

    def save_file_to_disk_and_session(self):
        self.save_file_to_disk()
        self.session.add_open_filename(self.get_current_buffer().filename)

    def save_file_to_disk(self):
        """ Save file """
        try:
            buf = self.get_current_buffer()
            buffer_has_filename = buf.has_filename()
            if buffer_has_filename:
                buffer_file = open(buf.filename, 'w')
                txt = buf.get_text_from_buffer()
                buffer_file.write(txt)
                if self.recent_manager:
                    self.recent_manager.add_full(
                        "file://" + urllib.quote(buf.filename),
                        {
                            'mime_type':'text/plain',
                            'app_name':'pyroom',
                            'app_exec':'%F',
                            'is_private':False,
                            'display_name':os.path.basename(buf.filename),
                        }
                    )
                buffer_file.close()
                buf.begin_not_undoable_action()
                buf.end_not_undoable_action()
                self.status.set_text(_('File %s saved') % buf.filename)
            else:
                self.save_file_as()
        except IOError, (errno, strerror):
            errortext = _('Unable to save %(filename)s.') % {
                'filename': buf.filename}
            if errno == 13:
                errortext += _(' You do not have permission to write to \
the file.')
            raise PyroomError(errortext)
        except:
            raise PyroomError(_('Unable to save %s\n') % buf.filename)
        buf.modified = False

    def save_file_as(self):
        """ Save file as """

        buf = self.get_current_buffer()

        chooser = gtk.FileChooserDialog('PyRoom', self.gui.window,
                gtk.FILE_CHOOSER_ACTION_SAVE,
                buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        chooser.set_default_response(gtk.RESPONSE_OK)
        if buf.has_filename():
            chooser.set_filename(buf.filename)
        res = chooser.run()
        if res == gtk.RESPONSE_OK:
            buf.filename = chooser.get_filename()
            self.save_file_to_disk()
        else:
            self.file_chooser_display_status_no_file_selected()
        chooser.destroy()

    def file_chooser_closed_with_no_file_selected(self):
        self.status.set_text(_('Closed, no files selected'))

    def word_count(self, buf):
        """ Word count in a text buffer """

        iter1 = buf.get_start_iter()
        iter2 = iter1.copy()
        iter2.forward_word_end()
        count = 0
        while iter2.get_offset() != iter1.get_offset():
            count += 1
            iter1 = iter2.copy()
            iter2.forward_word_end()
        return count

    def show_help(self):
        """ Create a new buffer and inserts help """
        buf = self.new_buffer()
        buf.begin_not_undoable_action()
        buf.set_text(HELP)
        buf.end_not_undoable_action()
        self.status.set_text("Displaying help. Press control W to exit and \
continue editing your document.")

    def new_buffer(self):
        """ Create a new buffer """
        buf = UndoableBuffer()
        self.buffers.insert(self.current + 1, buf)
        buf.place_cursor(buf.get_end_iter())
        self.next_buffer()
        return buf

    def close_dialog(self):
        """ask for confirmation if there are unsaved contents"""
        buf = self.get_current_buffer()
        if buf.modified:
            self.gui.close_buffer_dialog.show()
        else:
            self.close_current_buffer()

    def close_buffer_cancel_button_handler(self, widget, data=None):
        """dialog has been canceled"""
        self.gui.close_buffer_dialog.hide()

    def close_buffer_close_without_save_button_handler(self, widget, data=None):
        """don't save before closing"""
        self.gui.close_buffer_dialog.hide()
        self.close_current_buffer()

    def close_buffer_save_button_handler(self, widget, data=None):
        """save when closing"""
        self.gui.close_buffer_dialog.hide()
        self.save_file_to_disk()
        self.close_current_buffer()

    def close_current_buffer(self):
        """ Close current buffer """
        autosave_fname = autosave.get_autosave_filename(
            self.get_current_buffer().filename
        )
        if os.path.isfile(autosave_fname):
            try:
                os.remove(autosave_fname)
            except OSError:
                raise PyroomError(_('Could not delete autosave file.'))
        if len(self.buffers) > 1:
            self.session.remove_open_filename(
                self.get_current_buffer().filename
            )
            self.buffers.pop(self.current)
            self.current = min(len(self.buffers) - 1, self.current)
            self.set_buffer(self.current)
        else:
            quit()

    def set_buffer(self, index):
        """ Set current buffer """

        if index >= 0 and index < len(self.buffers):
            self.current = index
            buf = self.get_current_buffer()
            self.gui.show_text_buffer(buf.text_buffer)
            self.gui.show_changed_buffer_status(self.current + 1, buf.filename)


    def next_buffer(self):
        """ Switch to next buffer """

        if self.current < len(self.buffers) - 1:
            self.current += 1
        else:
            self.current = 0
        self.set_buffer(self.current)
        self.gui.place_cursor_at_start_of_buffer(self.get_current_buffer().get_insert())

    def prev_buffer(self):
        """ Switch to prev buffer """

        if self.current > 0:
            self.current -= 1
        else:
            self.current = len(self.buffers) - 1
        self.set_buffer(self.current)
        self.gui.place_cursor_at_start_of_buffer(self.get_current_buffer().get_insert())

    def save_dialog_or_quit_editor(self):
        count = self.count_modified_buffers()
        if count > 0:
            self.show_quit_dialog()
        else:
            self.quit()

    def count_modified_buffers(self):
        count = 0
        for buf in self.buffers:
            if buf.modified:
                count = count + 1
        return count

    def quit_dialog_cancel_button(self, widget, data=None):
        """don't quit"""
        self.hide_quit_dialog()

    def quit_dialog_save_button_handler(self, widget, data=None):
        """save before quitting"""
        self.hide_quit_dialog()
        for buffer in self.buffers:
            if buffer.modified:
                self.ask_for_filename_and_save_buffer(buffer)
        self.quit()

    def ask_for_filename_and_save_buffer(self, buf):
        if buf.filename == FILE_UNNAMED:
            self.save_file_as()
        else:
            self.save_file_to_disk()

    def quit_dialog_close_button_handler(self, widget, data=None):
        """really quit"""
        self.gui.quitdialog.hide()
        self.quit_editor()

    def quit_editor(self):
        self.quit()

    def hide_quit_dialog(self):
        self.gui.quitdialog.hide()

    def show_quit_dialog(self):
        self.gui.quitdialog.show()

    def quit(self):
        """cleanup before quitting"""
        autosave.stop_autosave(self)
        self.gui.quit()

    def get_current_buffer(self):
        """
        :rtype : UndoableBuffer
        """
        return self.buffers[self.current]

    def supercede_gui(self, gui):
        self.gui = gui


class VimEmulator(object):

    COMMAND_MODE = 'COMMAND_MODE_MAGIC_STRING'
    INSERT_MODE = 'INSERT_MODE_MAGIC_STRING'

    def __init__(self):
        self.mode = self.COMMAND_MODE
        pass

    def toggle_mode(self):
        if self.mode == self.COMMAND_MODE:
            self.mode = self.INSERT_MODE
        else:
            self.mode = self.COMMAND_MODE

    def in_command_mode(self):
        return self.mode == self.COMMAND_MODE

    def in_insert_mode(self):
        return self.mode == self.INSERT_MODE

class KeyPressDispatch(object):
    def __init__(self):
        pass
