import sys
from pathlib import Path
from tempfile import mkdtemp

from azureml.pipeline.wrapper.dsl.module import ModuleExecutor
from azureml.pipeline.wrapper import dsl
from azureml.core.run import Run

@dsl.module(
    job_type="basic",
    name="multiply"
)
def multiply(
        left: Path = Path('.'),
        right: Path = Path('.')
) -> Path:
    l = float(Path(left.resolve() / f'data').read_text().strip())
    r = float(Path(right.resolve() / f'data').read_text().strip())
    print('left = ', l)
    print('right = ', r)

    result = l * r
    run = Run.get_context()
    run.log('result', result)
    run.flush()

    output_path = Path(mkdtemp())
    with open(output_path / f'data', 'w') as fout:
        fout.write(str(result))
    return output_path


if __name__ == "__main__":
    ModuleExecutor(multiply).execute(sys.argv)
