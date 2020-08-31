import sys
import unittest
from pathlib import Path

from azureml.core import Workspace
from azureml.pipeline.wrapper import Module

# The following line adds source directory to path.
sys.path.insert(0, str(Path(__file__).parent.parent))
from concat_two_files_entry import concat_two_files


class TestConcatTwoFilesEntry(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.workspace = Workspace.from_config(str(Path(__file__).parent.parent / 'config.json'))
        cls.base_path = Path(__file__).parent.parent / 'data'

    def prepare_inputs(self) -> dict:
        # Change to your own inputs
        return {'input1': str(self.base_path / 'concat_two_files_entry' / 'inputs' / 'input1'),'input2': str(self.base_path / 'concat_two_files_entry' / 'inputs' / 'input2')}

    def prepare_outputs(self) -> dict:
        # Change to your own outputs
        return {'concatenated': str(self.base_path / 'concat_two_files_entry' / 'outputs' / 'concatenated')}

    def prepare_parameters(self) -> dict:
        # Change to your own parameters
        return {'append_line_break': False}

    def prepare_arguments(self) -> dict:
        # If your input's type is not Path, change this function to your own type.
        result = {}
        result.update(self.prepare_inputs())
        result.update(self.prepare_outputs())
        result.update(self.prepare_parameters())
        return result

    def test_module_from_func(self):
        # This test calls concat_two_files from cmd line arguments.
        local_module = Module.from_func(self.workspace, concat_two_files)
        module = local_module()
        module.set_inputs(**self.prepare_inputs())
        module.set_parameters(**self.prepare_parameters())
        status = module.run(use_docker=True)
        self.assertEqual(status, 'Completed', 'Module run failed.')

    def test_module_func(self):
        # This test calls concat_two_files from parameters directly.
        concat_two_files(**self.prepare_arguments())
