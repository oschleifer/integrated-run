import os

# Paths
full_input_file = "../input/cgfiles_100.csv"
partial_input_dir = "../input/partial_files"
os.makedirs(partial_input_dir, exist_ok=True)

line_counts = [1] + list(range(5, 101, 5))

with open(full_input_file, "r") as f:
    all_lines = f.readlines()

for count in line_counts:
    subset_file = os.path.join(partial_input_dir, f"martinifiles_{count}.csv")
    # Write subset of lines
    with open(subset_file, "w") as sf:
        sf.writelines(all_lines[:count])

