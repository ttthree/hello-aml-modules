from __future__ import print_function

import argparse
from azureml.core.run import Run
import GPUtil
import psutil
import torch
from typing import Dict, Iterable
import horovod.torch as hvd

def cpu_usage() -> Dict[str, float]:
    '''
    Return CPU memory and usage statistics as a dictionary mapping metric names
    to percentages (floats on a scale of 0 to 100).

    https://stackoverflow.com/a/2468983
    '''
    result = {}

    result['system_ram'] = psutil.virtual_memory().percent
    result['system_cpu'] = psutil.cpu_percent(interval=1)

    percentages = psutil.cpu_percent(interval=1, percpu=True)
    # https://stackoverflow.com/a/522578
    for i, p in enumerate(percentages):
        result[f'system_cpu_{i}'] = p

    return result


def gpu_usage() -> Dict[str, float]:
    '''
    Get CPU usage.
    '''
    result = {}
    gpus = GPUtil.getGPUs()

    for i, gpu in enumerate(gpus):
        usage = gpu.load # / gpu.memoryTotal * 100
        result[f'system_gpu_{i}'] = usage

    return result


def system_usage() -> Dict[str, float]:
    '''
    https://stackoverflow.com/a/26853961
    '''
    return {**cpu_usage(), **gpu_usage()}


if __name__ == '__main__':
    hvd.init()
    print("Mpi rank: ", hvd.rank(), " size: ", hvd.size(), " local rank: ", hvd.local_rank())

    parser = argparse.ArgumentParser()
    parser.add_argument('--size', default=15_000, type=int)
    parser.add_argument('--iterations', default=2000, type=int)
    args = parser.parse_args()

    print('Hi there!')
    n_gpu = torch.cuda.device_count()
    gpus = list(range(n_gpu))
    metrics = system_usage()

    run = Run.get_context()

    for i in range(args.iterations):
        print(f'Iteration {i} / {args.iterations}.')
        tensors = {}
        size = 10000 #int(args.size * (i + 1.0) / args.iterations)
        print(f'Tensor size: {size}x{size}.')
        for gpu in gpus:
            tensors[i] = torch.rand([size, size]).to(gpu)
            for j in range(args.iterations*100000):
                torch.prod(tensors[i], 0)
                if j % 100000 == 0:
                    metrics = system_usage()
                    metrics['size'] = size
                    for name, value in metrics.items():
                        run.log(name, value)
                        print(metrics)
    