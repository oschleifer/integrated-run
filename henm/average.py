import os
import numpy as np
from collections import defaultdict

def average_results(output_dir, num_runs):
    """
    Average cgk_{i}.dat files in output_dir and write cgk_avg.dat.

    Assumes mass.dat is identical across runs and doesn't need averaging.
    """
    data_dict = defaultdict(list)

    for i in range(1, num_runs + 1):
        filename = os.path.join(output_dir, f"cgk_{i}.dat")
        if not os.path.isfile(filename):
            print(f"Warning: {filename} not found. Skipping.")
            continue

        with open(filename, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) != 4:
                    continue  # skip malformed lines
                i_val, j_val = map(int, parts[:2])
                k, f_val = map(float, parts[2:])
                data_dict[(i_val, j_val)].append((k, f_val))

    output_path = os.path.join(output_dir, "cgk_avg.dat")
    with open(output_path, "w") as out:
        for (i_val, j_val), values in sorted(data_dict.items()):
            ks, fs = zip(*values)
            avg_k = np.mean(ks)
            avg_f = np.mean(fs)
            out.write(f"{i_val:4d} {j_val:4d} {avg_k:10.4f} {avg_f:10.4f}\n")

    print(f"Wrote averaged cgk to: {output_path}")
