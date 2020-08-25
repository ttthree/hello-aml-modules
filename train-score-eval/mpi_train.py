from __future__ import print_function
from datetime import datetime

import horovod.torch as hvd
import socket
import argparse
import pathlib
from azureml.core.run import Run
import numpy as np
import time
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

print("hostname: ", socket.gethostname(), " host ip: ", socket.gethostbyname(socket.gethostname()))

hvd.init()
print("Mpi rank: ", hvd.rank(), " size: ", hvd.size(), " local rank: ", hvd.local_rank())

parser = argparse.ArgumentParser("train")
parser.add_argument("--training_data", type=str, help="Path to training data")
parser.add_argument("--max_epochs", type=int, help="Max # of epochs for the training")
parser.add_argument("--learning_rate", type=float, help="Learning rate")
parser.add_argument("--model_output", type=str, help="Path of output model")
parser.add_argument("--run_for_minutes", type=int, help="How many minutes to run this sample module")

args = parser.parse_args()

lines = [f'Training data path: {args.training_data}', f'Max epochs: {args.max_epochs}', f'Learning rate: {args.learning_rate}', f'Model output path: {args.model_output}']

pathlib.Path(args.model_output).parent.absolute().mkdir(parents=True, exist_ok=True)
with open(args.model_output + "/output", 'w') as file:
    for line in lines:
        print(line)
        file.write(line + "\n")

# Log a few metrics
run = Run.get_context()

for accuracy in np.arange(0.0, 1.0, 0.01):
    run.log('accuracy', accuracy)

# Eating memory gradually for some time ...
#mem = []
#for i in range(1, 300):
#    time.sleep(1)
#    mem.append(' ' * 512 * 1024)
#    print(len(mem * 512 * 1024), ' bytes used.')

n_gpu = torch.cuda.device_count()
gpus = list(range(n_gpu))
metrics = system_usage()

iterations = 1000000
start = time.time()
for i in range(iterations):
    print(f'Iteration {i} / {iterations}.')
    tensors = {}
    size = 10000
    print(f'Tensor size: {size}x{size}.')
    for gpu in gpus:
        tensors[i] = torch.rand([size, size]).to(gpu)
        for j in range(1000000):
            torch.prod(tensors[i], 0)
            if j % 100000 == 0:
                metrics = system_usage()
                metrics['size'] = size
                for name, value in metrics.items():
                    run.log(name, value)
                    print(metrics)
                now = time.time()
                if (now - start > args.run_for_minutes * 60):
                    print("Completing ...")
                    exit(0)