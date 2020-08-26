import sys
import time

from azureml.pipeline.wrapper.dsl.module import ModuleExecutor
from azureml.pipeline.wrapper import dsl


@dsl.module(
    name="sleep_infinity"
#    custom_image='ttthree/burngpu:latest'
)
def sleep_infinity(
):
    while True:
        time.sleep(60)


if __name__ == '__main__':
    ModuleExecutor(sleep_infinity).execute(sys.argv)
