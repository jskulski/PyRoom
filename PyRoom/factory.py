
from PyRoom.basic_edit import BasicEdit
from PyRoom.preferences import PyroomConfig
from PyRoom.preferences import Preferences
from PyRoom.session import PrivateSession
from PyRoom.session import FileStoreSession
from PyRoom.gui import GUI
from PyRoom.gui import MockGUI
from PyRoom.gui import MockPreferences


class Factory(object):

    def create_new_editor(self, pyroom_config):
        gui = self.create_gui(pyroom_config)
        session = self.create_new_session(pyroom_config)
        preferences = self.create_new_preferences(pyroom_config, gui)
        return BasicEdit(
            pyroom_config=pyroom_config,
            gui=gui,
            session=session,
            preferences=preferences
        )

    def create_new_session(self, pyroom_config):
        if pyroom_config.get('session', 'private') == '1':
            session = PrivateSession()
        else:
            session = FileStoreSession(pyroom_config.get('session', 'filepath'))
        return session

    def create_gui(self, pyroom_config):
        return MockGUI()
        # return GUI(pyroom_config)
    
    def create_new_preferences(self, pyroom_config, gui):
        return MockPreferences()
        # return Preferences(gui, pyroom_config)
