import sys
from azureml.pipeline.wrapper.dsl.module import ModuleExecutor,\
    InputDirectory, OutputDirectory
from azureml.pipeline.wrapper import dsl
from azureml.pipeline.wrapper.dsl._notebook import execute_notebook


@dsl.module(
    name='concat_two_files',
    version='0.1',
    namespace='microsoft.com/azureml/samples',
    is_deterministic=True,
)
def concat_two_files(
    input1: InputDirectory(type='AnyDirectory', name='input1'),
    input2: InputDirectory(type='AnyDirectory', name='input2'),
    concatenated: OutputDirectory(type='AnyDirectory', name='concatenated'),
    append_line_break: bool = False,
):
    execute_notebook(
        'concat_two_files.ipynb',
        'concat_two_files.out.ipynb',
        dict(
            input1=input1,
            input2=input2,
            concatenated=concatenated,
            append_line_break=append_line_break,))


if __name__ == '__main__':
    ModuleExecutor(concat_two_files).execute(sys.argv)
