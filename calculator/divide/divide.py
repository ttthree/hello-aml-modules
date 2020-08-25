import sys
from pathlib import Path

from azureml.pipeline.wrapper.dsl.module import ModuleExecutor, InputDirectory, OutputDirectory
from azureml.pipeline.wrapper import dsl


@dsl.module(
    name="divide"
)
def divide(
        output_dir: OutputDirectory(),
        input_dir: InputDirectory() = '.',
        str_param='some_string',
):
    print(f'input_dir: {Path(input_dir).resolve()}')
    print(f'str_param: {str_param}')
    output_dir = Path(output_dir)
    with open(output_dir / f"output.txt", 'w') as fout:
        fout.write(str_param)


if __name__ == '__main__':
    ModuleExecutor(divide).execute(sys.argv)
