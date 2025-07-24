#!/bin/bash
#BSUB -J refine_XX
#BSUB -o out_files/refine_XX.out
#BSUB -e out_files/refine_XX.err
#BSUB -G cancer
#BSUB -nnodes 2
#BSUB -W 120
#BSUB -q pdebug

len=XX
INPUT=input/partial_files/martinifiles_${len}.csv

echo "Running for $INPUT"
pwd

source ~/.mummi/config.mummi.sh
source $MUMMI_APP/setup/setup.env.sh
spack load /nxpxh42
command -v gmx
pip install .

mkdir -p output

start=$(date +%s)

python3 -m henm.pipeline \
    --infile $INPUT \
    --out output/ \
    --lammps lammps/ \
    --stride 1

end=$(date +%s)
runtime=$((end - start))

echo "${len},${runtime}" >> filetimes.txt

