import os
import subprocess
import time

# Command template
base_command = (
    "python -m henm.pipeline "
    "--inputs /p/gpfs1/subramanian8/sims-cg/structure_iter00_traj004_f000000000017/lipids-water-eq4.gro "
    "/p/gpfs1/subramanian8/sims-cg/structure_iter00_traj004_f000000000017/structure_iter00_traj004_f000000000017.xtc "
    "--out output/ --lammps lammps/ --stride {stride}"
)

# Strides to test
strides = [1, 2, 5, 10, 25, 50, 75, 100, 200]

# Output timing file
timing_file = "timings.csv"

# Run each command and record time
with open(timing_file, mode="w", newline="") as f:
    f.write("stride,time_seconds\n")
    for stride in strides:
        command = base_command.format(stride=stride)
        print(f"Running stride={stride}")
        start_time = time.time()
        subprocess.run(command, shell=True)
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"Stride {stride} took {elapsed:.2f} seconds")
        f.write(f"{stride},{elapsed:.2f}\n")

print(f"Finished running all strides. Timing results saved to {timing_file}")

