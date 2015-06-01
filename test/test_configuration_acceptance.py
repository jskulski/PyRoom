from unittest import TestCase

import sys
sys.path.append('../PyRoom')

# mock out gettext
import __builtin__
__builtin__._ = lambda str: str

import os
import tempfile
import shutil
import uuid

from PyRoom.preferences import PyroomConfigFileBuilderAndReader

class TestConfigurationAcceptanceTest(TestCase):
    
    def setUp(self):
        self.configuration_directory = os.path.join('/tmp/pyroom', str(uuid.uuid4()))
        self.pyroom_config_file_builder_and_reader = PyroomConfigFileBuilderAndReader(
            configuration_directory=self.configuration_directory)

    def tearDown(self):
        if os.path.isdir(self.configuration_directory):
            shutil.rmtree(self.configuration_directory)

    def test_can_inject_config_directory(self):
        self.assertEquals(
            self.pyroom_config_file_builder_and_reader.conf_dir,
            self.configuration_directory
        )

    def test_does_not_modify_existing_configuration(self):
        tmp_dir = tempfile.mkdtemp()
        conf_file_path = os.path.join(tmp_dir, 'pyroom.conf')
        conf_file = open(conf_file_path, 'w')
        conf_file.write(self.customized_config_contents)
        conf_file.close()

        self.pyroom_config_file_builder_and_reader = PyroomConfigFileBuilderAndReader(
            configuration_directory=tmp_dir)

        config_file_contents = self.read_file_into_string(conf_file_path)
        self.assertEquals(self.customized_config_contents, config_file_contents)

    def test_creates_a_pyroom_conf_file_with_default_configuration(self):
        config_file_path = os.path.join(self.configuration_directory, 'pyroom.conf')
        self.assertTrue(os.path.isfile(config_file_path))

        config_file_contents = self.read_file_into_string(config_file_path)
        self.assertEquals(self.default_config_contents, config_file_contents)

    # Helper methods

    def read_file_into_string(self, file_path):
        with open(file_path, "r") as file:
            file_contents = file.read()
        return file_contents

    default_config_contents = """[visual]
use_font_type = custom
indent = 0
linespacing = 2
custom_font = Sans 12
theme = green
showborder = 1

[editor]
autosavetime = 2
autosave = 0
vim_emulation_mode = 0

"""

    customized_config_contents = """[visual]
use_font_type = custom
indent = 8
linespacing = 8
custom_font = Sans 22
theme = blue
showborder = 0

[editor]
autosavetime = 20
autosave = 1
vim_emulation_mode = 1

"""
