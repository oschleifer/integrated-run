#!/usr/bin/env python3

import sys
import os
import subprocess
import math
import glob

# paths to files used
include_path = "../exe-files/include"
exe_path = "../exe-files"

# copying the files from the "include" directory
subprocess.call(f"cp {include_path}/* .", shell=True)
# restoring the original "cg.xyz" file
subprocess.call("cp cg1.xyz cg.xyz", shell=True)

numargs = len(sys.argv)
currDir = os.getcwd()

# if during the iterations any k_ij becomes negative, then it is immediately replaced by the following value:
mink = 0.001

# TODO this is so weird
if numargs != 7 and numargs != 6:
    raise SystemExit("usage: fluc-match-8f.py initial_k_file fluctuation_file num_sites max_iter bFixed(0 or 1) (kfixed_file)")

# bondfile
kinitialfile = sys.argv[1]
flucfile = sys.argv[2]
numcgsites = int(sys.argv[3])
max_iter = int(sys.argv[4])
bFixed = int(sys.argv[5])

print(max_iter)

if bFixed == 1:
    kfixedfile = sys.argv[6]

numattypes = numcgsites

print(f"Input params:\n bond file: {kinitialfile}\n fluctuations: {flucfile}\n number of CG sites / atoms / pseudoatoms: {numcgsites}\n maximum number of iterations: {max_iter}\n fixed bonds: ")
if bFixed == 1:
    print(f"yes\nfixed bond file: {kfixedfile}\n")
else:
    print("no\n")

# initialize spring constant arrays and bondlist
# 2D array of size (40, 40) storing 0/1 if bond exists between 2 sites
bondlist = [[0] * (numcgsites) for _ in range(numcgsites)]
# number of bonds for each site (length 40)
nbonds = [0] * (numcgsites)
# number of "weakened" bonds for each site (length 40)
dn = [0] * (numcgsites)
# bond index of the max k for each site (length 40)
maxb = [0] * (numcgsites)
# value of max k for each site (length 40)
kbmax = [0] * (numcgsites)

# TODO: it might make more sense to store k's in a dict or 2D a
# start site (NOT index) of each bond (length 780)
endA = []
# end site (NOT index) of each bond (length 780)
endB = []
# spring constant of each bond (length 780)
k = []
# distance of each bond (length 780)
# TODO: not actually used for any computation
d_0 = []

# reading bond data
with open(kinitialfile) as f:
    # TODO: we don't actually need ibond
    ibond = 0
    for line in f:
        ibond += 1
        site1, site2, dist, k_init = line.split()
        site1, site2 = int(site1), int(site2)
        
        # use site1 - 1 and site2 - 1 as indices of the array
        bondlist[site1 - 1][site2 - 1] = 1
        bondlist[site2 - 1][site1 - 1] = 1
        nbonds[site1 - 1] += 1
        nbonds[site2 - 1] += 1
        
        endA.append(site1)
        endB.append(site2)
        d_0.append(float(dist))
        k.append(float(k_init))
        
totalbonds = ibond
knew = [0] * totalbonds
assert totalbonds == len(k) == 780
print(f" number of bonds (springs): {totalbonds}\n")

# read bond fluctuations from the fluctuation file (length 780)
rmsflucs = []
# array storing 0/1 whether the bond can be broken (length 780)
bbond = []

with open(flucfile) as f:
    ibond = 0
    for line in f:
        site1, site2, fluc = line.split()
        site1, site2 = int(site1), int(site2)
        if bondlist[site1 - 1][site2 - 1] == 1:
            ibond += 1
            rmsflucs.append(float(fluc))
            bbond.append(0)
        else:
            raise ValueError("fluctuation info does not match bond-file")

assert len(rmsflucs) == len(bbond) == 780

print("done reading input.\nmaking gromacs input\n")

# copying the initial k's to the hetero-enm bondfile
with open("cgk.dat", "w") as cgkfc:
    ibond = 0
    # TODO: there may be a clearer way to write this
    for l in range(numcgsites - 1):
        for n in range(l + 1, numcgsites):
            if bondlist[l][n] == 1:
                # write l+1 as the site number instead of index
                cgkfc.write(f"{l+1 :4d} {n+1 :4d} {d_0[ibond]:10.5f} {k[ibond]:10.5f}\n")
                ibond += 1

# create gromacs input files
with open("gro.in", "w") as grxin:
    grxin.write("#Control parameters for gromacs forcefield\n")
    grxin.write(f"#Number of sites\n{numcgsites}\n")
    grxin.write(f"#Number of Bonds\n{totalbonds}\n")
    grxin.write(f"#Number of atomtypes\n{numattypes}\n")
    grxin.write(f"#include path\n{currDir}\n")

with open("ffcharmm27.itp", "w") as grxff:
    grxff.write("#define _FF_CHARMM\n\n")
    grxff.write("[ defaults ]\n; nbfunc   combrule   gen-pairs   fudgeLJ   fudgeQQ\n")
    grxff.write("1   2   yes    1.0    1.0\n\n")
    grxff.write(f"#include \"{currDir}/ffcharmm27nb.itp\"\n")
    grxff.write(f"#include \"{currDir}/ffcharmm27bon.itp")

# call the program for preparation of some gromacs input files
subprocess.call(f"{exe_path}/mkgromax -imw mass.dat -ipr gro.in -iat cg.xyz -ibo {kinitialfile} -opr enm.itp -otp enm.top -ocr enm.gro -oat enm.atp", shell=True)


# prepare the input file for hetero-enm
with open("heteroenm.in", "w") as henin:
    henin.write("#Control parameters for hetero-enm\n")
    henin.write(f"#Number of (pseudo)atoms in the system\n{numcgsites}\n")
    numcgsitesX3 = numcgsites * 3
    henin.write(f"#The last number of normal mode we want to use (the first one is 7)\n{numcgsitesX3}\n")
    henin.write("#The temperature, in Kelvin\n310\n")

alpha = 0.5
iter = 0
residual = [[10e6] * (max_iter) for _ in range(totalbonds)]

###########################################
# iterations for k_ij matching start here #
###########################################

converge_flag = -1

while converge_flag < 0 and iter <= max_iter:

    # Run GROMACS for energy minimization
    print("running gromacs for energy minimization")
    subprocess.call("gmx grompp -f steep.mdp -p enm -c enm >& gr.log", shell=True)
    subprocess.call("gmx mdrun -ntmpi 1 -ntomp $OMP_NUM_THREADS >& md.log", shell=True)

    # Write XYZ structure file
    with open("cg.xyz", "w") as GRO:
        GRO.write(f"{numcgsites}\nautomatically generated by fluc-match-8f.pl script\n")
        
        with open("confout.gro", "r") as IN:
            iline = -2
            for line in IN:
                iline += 1
                if 0 < iline <= numcgsites:
                    parts = line.split()
                    GRO.write(f"{parts[1]:>4} {float(parts[3]) * 10:10.5f} {float(parts[4]) * 10:10.5f} {float(parts[5]) * 10:10.5f}\n")

    # Remove GROMACS backup and rename confout.gro
    os.rename("confout.gro", "enm.gro")
    backfiles = glob.glob("#*")
    for f in backfiles:
        os.remove(f)

    # Use the executable "hetero-enm" to compute bond fluctuations
    print(f"running heteroenm for iteration {iter}")
    subprocess.call(f"{exe_path}/hetero-enm -icf cg.xyz -ibn cgk.dat -ipr heteroenm.in -orf enm-bond-flucs.dat > enm.log", shell=True)

    # Read in the bond fluctuations
    enmflucs = {}
    with open("enm-bond-flucs.dat", "r") as IN:
        ibond = 0
        for line in IN:
            parts = line.split()
            # TODO: changed to 0-indexing. also why is enmflucs a dict?
            enmflucs[ibond] = float(parts[2])
            ibond += 1

    assert max(enmflucs.keys()) == totalbonds - 1 == 779

    if ibond != totalbonds :
        raise ValueError("number of bonds in enm-bond-flucs.dat does not match totalbonds")

    # Print fluctuations every 100 iterations
    if iter % 100 == 0:
        print(f"enm flucs for iteration {iter}")
        ibond = 0
        for l in range(numcgsites - 1):
            for n in range(l + 1, numcgsites):
                if bondlist[l][n] == 1:
                    print(f"{l + 1} {n + 1} {enmflucs[ibond]}")
                    ibond += 1

    # Compute the new spring constants and check for convergence
    
    # TODO: think this part is redundant, or maybe resetting is necessary
    for i in range(numcgsites):
        nbonds[i] = 0
        dn[i] = 0
        kbmax[i] = 0
        maxb[i] = 0

    print(f"{len(bbond)=}")
    for ibond in range(totalbonds):
        bbond[ibond] = 0

    print("computing new k's...")
    
    # this is a quick sanity check of 1 bond whether it's converging
    converge_flag = 1
    delta_flucs_sum = 0
    temptest = enmflucs[0]**2 - rmsflucs[0]**2
    print(f"squaretest {enmflucs[0]} {rmsflucs[0]} {temptest}")

    # iterating over all bonds
    for ibond in range(totalbonds):
        residual[ibond][iter] = (enmflucs[ibond] - rmsflucs[ibond])**2
        delta_flucs_sum += abs(enmflucs[ibond] - rmsflucs[ibond])
        delta_flucs = enmflucs[ibond]**2 - rmsflucs[ibond]**2

        if k[ibond] != 0.0:
            temp = 1.0 / k[ibond] - alpha * delta_flucs
            knew[ibond] = 1.0 / temp
            nbonds[endA[ibond] - 1] += 1
            nbonds[endB[ibond] - 1] += 1
            if knew[ibond] < 0.0:
                dn[endA[ibond] - 1] += 1
                dn[endB[ibond] - 1] += 1
        else:
            if k[ibond] == 0 and delta_flucs > 0:
                knew[ibond] = mink

    # Handle cases where all ks between two sites become negative
    
    # find the least negative (strongest) bond of each site
    ibond = 0
    for i in range(numcgsites):
        for j in range(i):
            if bondlist[i][j] == 1:
                ibond += 1
                if nbonds[i] - dn[i] <= 0:
                    if k[ibond] > kbmax[i]:
                        kbmax[i] = k[ibond]
                        maxb[i] = ibond
                if nbonds[j] - dn[j] <= 0:
                    if k[ibond] > kbmax[j]:
                        kbmax[j] = k[ibond]
                        maxb[j] = ibond

    assert ibond == totalbonds
    
    # preserve strongest bond
    for i in range(numcgsites):
        bbond[maxb[i]] = 1

    for ibond in range(totalbonds):
        if knew[ibond] < 0.0:
            if bbond[ibond] != 1:
                knew[ibond] = 0.0
            else:
                knew[ibond] = mink

    # Write the new k's to stdout
    print(f"; sum of abs difference between enm and observed flucs: {delta_flucs_sum}")
    print(f"spring constants for iteration {iter}:")
    for ibond in range(totalbonds):
        print(f"{ibond}\t{knew[ibond]}")
        diff = abs(knew[ibond] - k[ibond])
        if diff > 10e-4:
            converge_flag = -1
        k[ibond] = knew[ibond]

    assert len(k) == totalbonds
    
    # Write new spring constants into the itp and bond file
    print("writing new k's to itp file...")
    with open("enm.itp", "r") as IN, open("temp.itp", "w") as OUT:
        write_flag = -1
        # TODO: better way to keep track of bond index
        ibond = 0
        for line in IN:
            if write_flag > 0:
                parts = line.split()
                OUT.write(f"  {parts[0]}\t{parts[1]}\t{parts[2]}\t{parts[3]}")
                OUT.write(f" {float(k[ibond]) * 83600.8:10.4f}\n")
                ibond += 1
            elif write_flag < 0:
                OUT.write(line)
            if ";" in line and "ai" in line:
                write_flag = 1

    print("writing new k's to the file...")
    with open("cgk_temp.dat", "w") as CGKFC:
        ibond = 0
        for l in range(numcgsites - 1):
            for n in range(l + 1, numcgsites):
                if bondlist[l][n] == 1:
                    CGKFC.write(f"{l + 1:4d} {n + 1:4d}  {d_0[ibond]:8.4f}  {k[ibond]:10.4f}\n")
                    ibond += 1

    os.rename("temp.itp", "enm.itp")
    os.rename("cgk_temp.dat", "cgk.dat")

    if converge_flag > 0:
        print("exiting iteration loop...all fluc's converged within 10^-4")
    
    iter += 1

# Optional: Remove intermediate files if needed
# os.system("rm ffcharm27*")
# os.system("rm enm.*")
