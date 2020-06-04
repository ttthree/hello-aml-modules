import sys
from pathlib import Path
from tempfile import mkdtemp

from azureml.pipeline.wrapper.dsl.module import ModuleExecutor
from azureml.pipeline.wrapper import Pipeline, Module, dsl

@dsl.module(name='enter_num_manually', description='Put a number in parameter and this module will convert it to a file', job_type='basic')
def enter_num_manually(num='0') -> Path:
    output_path = Path(mkdtemp())
    with open(output_path / f'data', 'w') as fout:
        fout.write(num)
    return output_path

if __name__ == "__main__":
    ModuleExecutor(enter_num_manually).execute(sys.argv)