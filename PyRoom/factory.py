
from PyRoom.basic_edit import BasicEdit
from PyRoom.preferences import PyroomConfig
from PyRoom.session import PrivateSession
from PyRoom.session import FileStoreSession
from PyRoom.gui import GUI

class Factory(object):

    def __init__(self, pyroom_config=None):
        self.pyroom_config = pyroom_config if pyroom_config else PyroomConfig()
        self.editor = None
        self.gui = None
        self.session = None

    def create_editor(self, pyroom_config=None):
        if pyroom_config is None:
            pyroom_config = self.pyroom_config

        # Session Management
        if pyroom_config.get('session', 'private') == '1':
            session = PrivateSession()
        else:
            session = FileStoreSession(pyroom_config.get('session', 'filepath'))

        return BasicEdit(
            pyroom_config=pyroom_config,
            gui=self.create_gui(),
            session=session
        )

    def create_gui(self):
        if not self.gui:
            self.gui = GUI(
                self.pyroom_config
            )
