import shutil
import sys
import argparse
from os import listdir
from os.path import isfile, join
import math
import os

parser = argparse.ArgumentParser("merge")
parser.add_argument("--input_folder", type=str, help="Path of input folder")
parser.add_argument("--output_folder", type=str, help="Path of output folder")
parser.add_argument("--merge_count", type=int, help="Path of output folder")

args = parser.parse_args()

input_folder = args.input_folder
output_folder = args.output_folder
merge_count = args.merge_count

print("SystemLog: Reading from input folder %s"%args.input_folder)
print("SystemLog: Reading from output folder %s"%args.output_folder)
print("SystemLog: Merging every %d file together"%args.merge_count)
sys.stdout.flush()

total_files_processed = 0
onlyfiles = [os.path.abspath(join(input_folder, f)) for f in listdir(input_folder) if isfile(join(input_folder, f))]
total_files = len(onlyfiles)
total_merges = int(math.ceil(total_files/merge_count))
print("SystemLog: Total files in input_folder %d and total expected merged ones %d"% (total_files, total_merges))
sys.stdout.flush()

# This line should be added since in AzureML, output folder is not created.
os.makedirs(output_folder, exist_ok=True)

for merge_idx in range(total_merges):
    merged_file = open(os.path.abspath(os.path.join(output_folder, str(merge_idx))), 'wb')
    files_to_be_merged = onlyfiles[merge_idx * merge_count: (merge_idx + 1) * merge_count]
    #print(files_to_be_merged)
    for file_to_be_merged in files_to_be_merged:
        shutil.copyfileobj(open(file_to_be_merged, 'rb'), merged_file)
        total_files_processed += 1
        if total_files_processed % 1000 == 0:
            print("SystemLog: Total files processed %d"%total_files_processed)
            sys.stdout.flush()
print("Total files processed are %d and merged to %d files"%(total_files_processed, total_merges))
sys.stdout.flush()
