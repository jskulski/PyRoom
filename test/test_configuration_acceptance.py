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

    def test_can_inject_config_directory(self):
        injected_conf_dir_path = os.path.join(
            '/tmp/pyroom',
            str(uuid.uuid4()))

        pyroom_config_file_builder_and_reader = PyroomConfigFileBuilderAndReader(
            configuration_directory=injected_conf_dir_path)
        self.assertEquals(
            pyroom_config_file_builder_and_reader.conf_dir,
            injected_conf_dir_path
        )

        shutil.rmtree(injected_conf_dir_path)

    def test_creates_a_pyroom_conf_file_with_default_configuration(self):
        injected_conf_dir_path = os.path.join(
            '/tmp/pyroom',
            str(uuid.uuid4()))
        pyroom_config_file_builder_and_reader = PyroomConfigFileBuilderAndReader(
            configuration_directory=injected_conf_dir_path)

        config_file_path = os.path.join(injected_conf_dir_path, 'pyroom.conf')

        self.assertTrue(os.path.isfile(config_file_path))

        with open(config_file_path, "r") as config_file:
            config_file_contents = config_file.read()
        print config_file_contents

        expected_config_contents = """[visual]
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
        self.assertEquals(expected_config_contents, config_file_contents)

        shutil.rmtree(injected_conf_dir_path)
