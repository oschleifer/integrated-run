import os
import subprocess
import time

# Paths
full_input_file = "input/martinifiles.csv"
partial_input_dir = "input/partial_files"
os.makedirs(partial_input_dir, exist_ok=True)

# Output timing file
timing_file = "timings_pipeline.csv"

# Number of lines to test
line_counts = [1, 5, 10, 15, 20, 25, 75]

# Read all lines from full input
with open(full_input_file, "r") as f:
    all_lines = f.readlines()

# Run each test
with open(timing_file, mode="w", newline="") as f:
    f.write("lines,time_seconds\n")
    for count in line_counts:
        subset_file = os.path.join(partial_input_dir, f"martinifiles_{count}.csv")
        # Write subset of lines
        with open(subset_file, "w") as sf:
            sf.writelines(all_lines[:count])

        command = (
            f"python -m henm.pipeline "
            f"--infile {subset_file} "
            f"--out output/ "
            f"--lammps lammps/ "
            f"--stride 1"
        )

        print(f"Running with {count} lines")
        start_time = time.time()
        subprocess.run(command, shell=True)
        end_time = time.time()
        elapsed = end_time - start_time

        print(f"{count} lines took {elapsed:.2f} seconds")
        f.write(f"{count},{elapsed:.2f}\n")

print(f"Finished timing runs. Results saved to {timing_file}")

