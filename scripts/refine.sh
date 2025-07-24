#!/bin/bash
#BSUB -J integrated-run_job            # Job name
#BSUB -o integrated-run_job.out        # Output file
#BSUB -e integrated-run_job.err        # Error file
#BSUB -G cancer                        # Use the 'cancer' bank/project
#BSUB -nnodes 2                        # Number of nodes (change as needed)
#BSUB -W 120                           # Wall-clock time (10 minutes)
#BSUB -q pdebug                        # Use debug queue

# test command: 
# echo "Test job running on $(hostname)" && sleep 10

pwd 

# Set up environment
source ~/.mummi/config.mummi.sh
source $MUMMI_APP/setup/setup.env.sh
# load GROMACS
spack load /nxpxh42
echo "Loaded GROMACS"
command -v gmx
# installing henm package
pip install .

python3 -m henm.pipeline \
    	--infile input/partial_files/martinifiles_100.csv \
	--out output/ \
   	--lammps lammps/ \
        -- stride 1

echo "processed "$(wc -l input/partial_files/martinifiles_100.csv)" files"

