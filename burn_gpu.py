import numpy as np
import torch
import sys
import time
import logging

logging.basicConfig(format='[%(asctime)s]\t\t%(message)s', level=logging.DEBUG)

gpu = int(sys.argv[1])
minutes = int(sys.argv[2])

logging.info('Going to exhaust gpu #%s' % gpu)
mem_in_gb = torch.cuda.get_device_properties(0).total_memory / 1024 / 1024 / 1024
logging.info('GPU total memory = %s GiB' % mem_in_gb)

if mem_in_gb > 30:
    size = 70000
elif mem_in_gb > 20:
    size = 50000
elif mem_in_gb > 10:
    size = 40000
else:
    size = 30000

logging.info('So we are creating tensor with size %s x %s' % (size, size))

tensors = torch.rand([size, size]).to(gpu)
logging.info('Tensor loaded to gpu')
i = 0
start = time.time()
while True:
    i += 1
    torch.prod(tensors, 0)
    if (i % 10000 == 0):
        logging.info('%s iterations done' % i)
        now = time.time()
        if (now - start > minutes * 60):
            logging.info("Completing as more than %s minutes elapsed ..." % minutes)
            exit(0)