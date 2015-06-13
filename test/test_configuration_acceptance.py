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
from PyRoom.preferences import PyroomConfig

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

    def test_pyroom_config_default_object_is_the_same_as_the_default_pyroom_file_boject(self):
        self.maxDiff = None
        self.assertEquals(
            self.pyroom_config_file_builder_and_reader.config.__dict__,
            PyroomConfig().__dict__)

    # Helper methods
    def read_file_into_string(self, file_path):
        with open(file_path, "r") as file:
            file_contents = file.read()
        return file_contents


