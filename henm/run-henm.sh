#!/bin/bash

# Default value
NUMFILES=0

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --numfiles) NUMFILES="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

if [[ $NUMFILES -le 0 ]]; then
    echo "Usage: $0 --numfiles <number_of_trajectories>"
    exit 1
fi

echo "Starting job"

# Setting up environment for Lassen
# env | grep MUMMI
# source /usr/workspace/mummiusr/mummi-spack/spack/0.21/share/spack/setup-env.sh
# echo "Setup environment complete."

# echo "Loading GROMACS..."
# spack load /nxpxh42
# echo "Loaded GROMACS"
# command -v gmx
# export OMP_NUM_THREADS=8

# Aligning trajectories
echo "Aligning trajectories..."

cd run-align
for ((i=1; i<=NUMFILES; i++)); do
    python3 align-mda.py \
        --struc ../../gromacs/sim_${i}/confout.gro \
        --traj ../../gromacs/sim_${i}/traj_comp.trr \
        --out1 traj_sup_${i}.pdb \
        --out2 struc_ave_${i}.pdb
done

# Running hENM refinement
cd ../run-fluc
for ((i=1; i<=NUMFILES; i++)); do
    bash commands.sh \
        --in1 ../run-align/traj_sup_${i}.pdb \
        --in2 ../run-align/struc_ave_${i}.pdb \
        --out1 ../output/mass_${i}.dat \
        --out2 ../output/cgk_${i}.dat
done

# Averaging results
cd ../output
python3 average.py "$NUMFILES"

# Optionally generate LAMMPS input
# cd ../../lammps/lammps-input
# python3 get_data.py lammpsdata.dat
# python3 get_bond_coeff.py lammpsbondcoeff.dat

echo "Done"
# deactivate
echo "Finished"