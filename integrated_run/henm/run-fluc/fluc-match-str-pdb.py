#!/usr/bin/env python3

import sys
import os
import math

# INPUT PARSING
path_to_amino_acid_masses = "../input-files"

if len(sys.argv) != 8:
    raise SystemExit("usage: average.pdb trj.pdb ba.dat bondfile flucfile cutoff_distance k_initial")

PDB = sys.argv[1]
trajfile = sys.argv[2]
bafile = sys.argv[3]
bondfile = sys.argv[4]
flucfile = sys.argv[5]
cutoff = float(sys.argv[6])
kini = float(sys.argv[7])

print("Input params:")
print(f"average structure: {PDB}")
print(f"trajectory file: {trajfile}")
print(f"CG mapping: {bafile}")
print(f"bondfile: {bondfile}")
print(f"fluctuations file: {flucfile}")
print(f"cutoff: {cutoff} Angstroms, initial k: {kini}\n")

# make a hashmap of amino acid to mass
masses = {}
with open(f"{path_to_amino_acid_masses}/amino-acid-masses.txt") as f:
    for line in f:
        parts = line.split()
        masses[parts[1]] = float(parts[3])

# read in the CG mapping
residuemap = []
cgmass = []
numcgsites = 0

with open(bafile) as f:
    ba = 0
    for line in f:
        parts = line.split()
        if parts:
            ba += 1
            residuemap.append(int(parts[0]))
            cgmass.append(0)
            numcgsites = max(numcgsites, int(parts[0]))

print(f"found {numcgsites} CG sites")

# read sequence info from the PDB and assign masses to CG sites
resmass = {}
linecount = 0

with open(PDB) as f:
    for line in f:
        if line.startswith("ATOM"):
            linecount += 1
            parts = line.split()
            sequence = parts[3]
            ba = residuemap[linecount - 1]
            flag = False
            for key in masses:
                if sequence == key:
                    flag = True
                    cgmass[ba - 1] += masses[key]
                    resmass[linecount] = masses[key]
            if not flag:
                raise ValueError(f"could not match residue type of residue {sequence}.")

numresidues = linecount
print(f"found {numresidues} residues(sites)")

# Write the masses of each site to a file
with open("mass.dat", "w") as massd:
    print("masses of CG sites:")
    inv_cgmass = []
    for i in range(numcgsites):
        print(f"{i+1}\t{cgmass[i]}")
        massd.write(f"C{i+1:<4}\t{cgmass[i]:12.6f}\n")
        inv_cgmass.append(1.0 / cgmass[i])

print("done with CG map.\n\nNow moving on to the trajectory:")

# initialize arrays of 0s with length =  # of residues
xcom = [0] * numresidues
ycom = [0] * numresidues
zcom = [0] * numresidues
xavgcom = [0] * numresidues
yavgcom = [0] * numresidues
zavgcom = [0] * numresidues

with open(bondfile, "w") as bonddat, open(flucfile, "w") as flucdat, open("cg1.xyz", "w") as struc:
    struc.write(f"{numcgsites}\nComment line\n")
    
    with open(trajfile) as f:
        frameindex = 1
        linecount = 0
        # out of range on this list

        for line in f:
            
            if line.startswith("NUMMDL"):
                num_frames = int(line.split()[1])
                # TODO: make these numpy arrays?
                xcomcoords = [[] for _ in range(num_frames)]
                ycomcoords = [[] for _ in range(num_frames)]
                zcomcoords = [[] for _ in range(num_frames)]
                
            if line.startswith("ATOM"):
                linecount += 1
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])

                cgsiteindex = residuemap[linecount - 1]

                xcom[cgsiteindex - 1] += resmass[linecount] * x
                ycom[cgsiteindex - 1] += resmass[linecount] * y
                zcom[cgsiteindex - 1] += resmass[linecount] * z

            if linecount == numresidues:
                inv_frame = 1.0 / frameindex
                frame_weight = (frameindex - 1.0) / frameindex

                print(numresidues, numcgsites)
                for i in range(numcgsites):
                    xcom[i] *= inv_cgmass[i]
                    ycom[i] *= inv_cgmass[i]
                    zcom[i] *= inv_cgmass[i]
                    
                    print(frameindex - 1)

                    xcomcoords[frameindex - 1].append(xcom[i])
                    ycomcoords[frameindex - 1].append(ycom[i])
                    zcomcoords[frameindex - 1].append(zcom[i])

                    xavgcom[i] = xcom[i] * inv_frame + xavgcom[i] * frame_weight
                    yavgcom[i] = ycom[i] * inv_frame + yavgcom[i] * frame_weight
                    zavgcom[i] = zcom[i] * inv_frame + zavgcom[i] * frame_weight

                    xcom[i] = 0
                    ycom[i] = 0
                    zcom[i] = 0

                linecount = 0
                frameindex += 1

    # print the average com of x y and z of each ucg site to file
    for i in range(numcgsites):
        struc.write(f"C{i+1:<5} {xavgcom[i]:12.6f} {yavgcom[i]:12.6f} {zavgcom[i]:12.6f}\n")

    numframes = frameindex - 1
    print(f"found {numframes} frames")

    # initialize the running avg variables
    davg = [[0] * numcgsites for _ in range(numcgsites)]
    dsqravg = [[0] * numcgsites for _ in range(numcgsites)]

    print("computing fluctuations")

    # compute avg length and fluc's of all possible bonds:
    for frame in range(numframes):
        for i in range(numcgsites):
            for j in range(i + 1, numcgsites):
                dx = xcomcoords[frame][i] - xcomcoords[frame][j]
                dy = ycomcoords[frame][i] - ycomcoords[frame][j]
                dz = zcomcoords[frame][i] - zcomcoords[frame][j]
                dist = math.sqrt(dx * dx + dy * dy + dz * dz)
                davg[i][j] = dist / (frame + 1) + davg[i][j] * (frame / (frame + 1))
                dsqravg[i][j] = dist * dist / (frame + 1) + dsqravg[i][j] * (frame / (frame + 1))

    deltasqr = [[0] * numcgsites for _ in range(numcgsites)]

    # subtract off the avg^2:
    for i in range(numcgsites):
        for j in range(i + 1, numcgsites):
            deltasqr[i][j] = dsqravg[i][j] - davg[i][j] * davg[i][j]

    # build up the topology of the network
    for i in range(numcgsites):
        for j in range(i + 1, numcgsites):
            if davg[i][j] < cutoff:
                rmsfluc = math.sqrt(deltasqr[i][j])
                bonddat.write(f"{i+1:4d} {j+1:4d}  {davg[i][j]:10.5f}  {kini:10.5f}\n")
                flucdat.write(f"{i+1:3d} {j+1:3d}  {rmsfluc:10.5f}\n")

# check for CG sites with small number of connections
print("\n")
for i in range(numcgsites):
    numbonds = sum(1 for j in range(numcgsites) if (i != j and davg[min(i, j)][max(i, j)] < cutoff))
    if numbonds < 3:
        print(f"warning: atom {i+1} has only {numbonds} bonds.")

os.system("cp cg1.xyz cg.xyz")
