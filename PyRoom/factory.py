
from PyRoom.basic_edit import BasicEdit
from PyRoom.preferences import PyroomConfig
from PyRoom.gui import GUI

class Factory(object):

    def __init__(self, pyroom_config):
        self.pyroom_config = pyroom_config if pyroom_config else PyroomConfig()
        self.editor = None
        self.gui = None

    def create_editor(self, pyroom_config=None):
        if pyroom_config is None:
            pyroom_config = self.pyroom_config

        if not self.editor:
            self.editor = BasicEdit(
                pyroom_config=pyroom_config,
                gui=self.create_gui()
            )

        return self.editor

    def create_gui(self):
        if not self.gui:
            self.gui = GUI(
                self.pyroom_config
            )
