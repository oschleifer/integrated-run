import os
import csv

# Root directory to search
root_dir = "/p/gpfs1/subramanian8/sims-cg/"

# Output CSV file
output_csv = "martinifiles.csv"

# Open the CSV file for writing
with open(output_csv, mode="w", newline="") as csvfile:
    writer = csv.writer(csvfile)

    # Walk through all subdirectories
    for dirname in os.listdir(root_dir):
        dirpath = os.path.join(root_dir, dirname)
        if os.path.isdir(dirpath):
            xtc_file = os.path.join(dirpath, f"{dirname}.xtc")
            if os.path.isfile(xtc_file):
                gro_path = os.path.join(dirpath, "lipids-water-eq4.gro")
                xtc_path = xtc_file
                writer.writerow([gro_path, xtc_path])

print(f"Finished writing {output_csv}")

