import unittest

import sys
sys.path.append('../PyRoom')

# mock out gettext
import __builtin__
__builtin__._ = lambda str: str

import tempfile

import editor_input
from PyRoom.basic_edit import BasicEdit
from PyRoom.basic_edit import VimEmulator
from PyRoom.preferences import PyroomConfig

class VimEmulationAcceptanceTest(unittest.TestCase):

    def setUp(self):
        self.pyroom_config = PyroomConfig()
        self.pyroom_config.set('editor', 'vim_emulation_mode', '1')
        self.pyroom_config.clear_session = 1
        self.basic_editor = BasicEdit(self.pyroom_config)

    def test_that_vim_emulation_mode_is_off_by_default_in_editor(self):
        self.assertEquals(
            '0',
            PyroomConfig().get('editor', 'vim_emulation_mode')
        )

    def test_that_we_can_type_normally_if_vim_emulation_mode_is_off(self):
        default_pyroom_config = PyroomConfig()
        default_pyroom_config.set('session', 'filepath', tempfile.NamedTemporaryFile().name)
        default_basic_editor = BasicEdit(default_pyroom_config)

        editor_input.type_key('i', default_basic_editor)
        buffer_text = editor_input.retrieve_current_buffer_text(default_basic_editor)

        self.assertEquals(buffer_text, 'i')

    def test_that_vim_emulator_object_is_not_created_in_editor(self):
        pyroom_config = PyroomConfig()
        pyroom_config.set('session', 'private', '1')
        default_basic_editor = BasicEdit(pyroom_config)
        self.assertIsNone(default_basic_editor.vim_emulator)

    def test_that_vim_emulator_is_created_if_turned_on_in_config(self):
        self.assertIsInstance(self.basic_editor.vim_emulator, VimEmulator)

    def test_that_typing_ihi_toggles_to_insert_mode_and_types_hi(self):
        editor_input.type_keys('ihi', self.basic_editor)
        buffer_text = editor_input.retrieve_current_buffer_text(self.basic_editor)

        self.assertEquals(buffer_text, 'hi')

    def test_escape_in_insert_mode_toggles_to_command_mode(self):
        editor_input.type_key('i', self.basic_editor)
        editor_input.type_key('Escape', self.basic_editor)

        self.assertTrue(self.basic_editor.vim_emulator.in_command_mode())
        self.assertFalse(self.basic_editor.vim_emulator.in_insert_mode())

    def test_user_is_notified_of_toggling_to_opposoite_modes(self):
        status_spy = StatusSpy()
        self.basic_editor.status = status_spy
        editor_input.type_key('i', self.basic_editor)
        self.assertTrue(status_spy.was_notified())


class StatusSpy(object):
    def __init__(self):
        self.notified = False

    def set_text(self, string, something_else):
        self.notified = True

    def was_notified(self):
        return self.notified

