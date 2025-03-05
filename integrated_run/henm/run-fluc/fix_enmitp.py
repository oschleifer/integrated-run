#!/usr/bin/env python3

ibond = 0
k = []

# Read 'cgk.dat' file and populate k array
with open("cgk.dat", "r") as infile:
    for line in infile:
        ibond += 1
        line_parts = line.split()
        k.append(float(line_parts[3]))

# Read 'enm.itp' file and write to 'temp.itp' file
write_flag = -1
ibond = 0

with open("enm.itp", "r") as infile, open("enm_lammps.itp", "w") as outfile:
    for line in infile:
        if write_flag > 0:
            ibond += 1
            line_parts = line.split()
            outfile.write(f"  {line_parts[0]}\t{line_parts[1]}\t{line_parts[2]}\t{line_parts[3]}")
            outfile.write(f" {k[ibond - 1] * 836.8:10.4f}\n")
        elif write_flag < 0:
            outfile.write(line)
        if ";" in line and "ai" in line:
            write_flag = 1

# Rename files (uncomment if needed)
# os.rename("temp.itp", "enm.itp")
# os.rename("cgk_temp.dat", "cgk.dat")
