import os
import numpy as np
from collections import defaultdict

def average_results(output_dir, num_runs):
    """
    Average cgk_{i}.dat and cg1_{i}.xyz files in output_dir and write cgk_avg.dat and cg1_avg.xyz.

    Assumes mass.dat is identical across runs and doesn't need averaging.
    """
    # Average cgk_{i}.dat files
    data_dict = defaultdict(list)

    for i in range(1, num_runs + 1):
        cgk_filename = os.path.join(output_dir, f"cgk_{i}.dat")
        if not os.path.isfile(cgk_filename):
            print(f"Warning: {cgk_filename} not found. Skipping.")
            continue

        with open(cgk_filename, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) != 4:
                    continue  # skip malformed lines
                i_val, j_val = map(int, parts[:2])
                k, f_val = map(float, parts[2:])
                data_dict[(i_val, j_val)].append((k, f_val))

    cgk_output_path = os.path.join(output_dir, "cgk_avg.dat")
    with open(cgk_output_path, "w") as out:
        for (i_val, j_val), values in sorted(data_dict.items()):
            ks, fs = zip(*values)
            avg_k = np.mean(ks)
            avg_f = np.mean(fs)
            out.write(f"{i_val:4d} {j_val:4d} {avg_k:10.4f} {avg_f:10.4f}\n")

    print(f"Wrote averaged cgk to: {cgk_output_path}")

    # Average cg1_{i}.xyz files
    xyz_data = []

    for i in range(1, num_runs + 1):
        cg1_filename = os.path.join(output_dir, f"cg1_{i}.xyz")
        if not os.path.isfile(cg1_filename):
            print(f"Warning: {cg1_filename} not found. Skipping.")
            continue

        with open(cg1_filename, "r") as f:
            lines = f.readlines()[2:]  # Skip the first two lines (header)
            coords = np.array([list(map(float, line.split()[1:])) for line in lines])
            xyz_data.append(coords)

    if xyz_data:
        avg_xyz = np.mean(xyz_data, axis=0)
        cg1_output_path = os.path.join(output_dir, "cg1_avg.xyz")
        with open(cg1_output_path, "w") as out:
            out.write(f"{len(avg_xyz)}\n")
            out.write("Averaged coordinates\n")
            for i, (x, y, z) in enumerate(avg_xyz):
                out.write(f"C{i} {x:10.4f} {y:10.4f} {z:10.4f}\n")

        print(f"Wrote averaged cg1 to: {cg1_output_path}")