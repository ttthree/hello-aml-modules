import sys
import unittest
from pathlib import Path

from azureml.core import Workspace
from azureml.pipeline.wrapper import Module

sys.path.append(str(Path(__file__).parent.parent))
from multiply import multiply


class TestMultiply(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.workspace = Workspace.from_config(str(Path(__file__).parent.parent / 'config.json'))
        cls.base_path = Path(__file__).parent
        cls.outputs = cls.base_path / 'outputs'

    def prepare_inputs(self) -> dict:
        # Change to your own inputs
        return {'left': str(self.base_path / 'inputs' / 'left'), 'right': str(self.base_path / 'inputs' / 'right')}

    def prepare_parameters(self) -> dict:
        # Change to your own parameters
        return {}

    def prepare_arguments(self) -> dict:
        # If your input's type is not Path, change this function to your own type.
        result = {}
        inputs = self.prepare_inputs()
        for input in inputs:
            inputs[input] = Path(inputs[input])
        result.update(inputs)
        result.update(self.prepare_parameters())
        return result

    def test_module_from_func(self):
        # This test calls multiply from cmd line arguments.
        local_module = Module.from_func(self.workspace, multiply)
        module = local_module()
        module.set_inputs(**self.prepare_inputs())
        module.set_parameters(**self.prepare_parameters())
        status = module.run(working_dir=str(self.outputs), use_docker=False)
        self.assertEqual(status, 'Completed', 'Module run failed.')

    def test_module_func(self):
        # This test calls multiply from parameters directly.
        result = multiply(**self.prepare_arguments())
        self.assertIsNotNone(result)
