
from PyRoom.basic_edit import BasicEdit
from PyRoom.preferences import PyroomConfig
from PyRoom.session import PrivateSession
from PyRoom.session import FileStoreSession
from PyRoom.gui import GUI

class Factory(object):

    def create_new_editor(self, pyroom_config):
        return BasicEdit(
            pyroom_config=pyroom_config,
            gui=self.create_gui(pyroom_config),
            session=self.create_new_session(pyroom_config)
        )

    def create_new_session(self, pyroom_config):
        if pyroom_config.get('session', 'private') == '1':
            session = PrivateSession()
        else:
            session = FileStoreSession(pyroom_config.get('session', 'filepath'))
        return session

    def create_gui(self, pyroom_config):
        return GUI(
            pyroom_config
        )
