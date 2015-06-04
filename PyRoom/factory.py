
from PyRoom.basic_edit import BasicEdit
from PyRoom.preferences import PyroomConfig

class Factory(object):

    def __init__(self):
        self.editor = None

    def create_editor(self, pyroom_config=None):
        if pyroom_config is None:
            pyroom_config = PyroomConfig()

        if not self.editor:
            self.editor = BasicEdit(
                pyroom_config=pyroom_config
                # gui=self.create_gui()
            )

        return self.editor

    # def create_gui(self):
    #     if not self.gui = GUI(
    #
    #     )
