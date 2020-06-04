from argparse import ArgumentParser
import pathlib
import time

parser = ArgumentParser()
parser.add_argument("--numinputs", type=int, help="# of inputs")
parser.add_argument("--numoutputs", type=int, help="# of outputs")
parser.add_argument("--paths", nargs="+", help="inputs and outputs (path)")

#args = parser.parse_args('--numinputs 2 --numoutputs 2 --paths test.1 test.2 test.3 test.4'.split())
args = parser.parse_args()

total = args.numinputs + args.numoutputs
if (len(args.paths) != total):
    error = f"Expect {total} inputs/outputs in total but found {len(args.paths)}"
    raise Exception(error)

lines = []
for i in range(0, args.numinputs):
    lines.append(args.paths[i])

for i in range(args.numinputs, total):
    pathlib.Path(args.paths[i]).parent.absolute().mkdir(parents=True, exist_ok=True)
    with open(args.paths[i], 'w') as file:
        for line in lines:
            print(line)
            file.write(line + "\n")

# Eating memory gradually for some time ...
mem = []
for i in range(1, 100):
    time.sleep(1)
    mem.append(' ' * 512 * 1024)
    print(len(mem * 512 * 1024), ' bytes used.')