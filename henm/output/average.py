import sys
import numpy as np
from collections import defaultdict
import os

def parse_args(args):
    if len(args) < 2:
        print("Usage: python average.py <num_files> OR python average.py cgk_1.dat cgk_2.dat ...")
        sys.exit(1)

    if args[1].isdigit():
        n = int(args[1])
        return [f"cgk_{i}.dat" for i in range(1, n + 1)]
    else:
        return args[1:]

data_dict = defaultdict(list)
files = parse_args(sys.argv)

# Read each input file and collect values
for filename in files:
    if not os.path.isfile(filename):
        print(f"Warning: {filename} not found. Skipping.")
        continue
    with open(filename, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 4:
                continue  # skip malformed lines
            i, j = map(int, parts[:2])
            k, f_val = map(float, parts[2:])
            data_dict[(i, j)].append((k, f_val))

# Compute the average
with open("cgk_avg.dat", "w") as out:
    for (i, j), values in sorted(data_dict.items()):
        ks, fs = zip(*values)
        avg_k = np.mean(ks)
        avg_f = np.mean(fs)
        out.write(f"{i:4d} {j:4d} {avg_k:10.4f} {avg_f:10.4f}\n")
