echo "Starting job"

# source ~/.mummi/config.mummi.sh

# env | grep MUMMI

source /usr/workspace/mummiusr/mummi-spack/spack/0.21/share/spack/setup-env.sh

# source $MUMMI_APP/setup/setup.env.sh

echo "Setup environment complete."

echo "Loading GROMACS..."
spack load /nxpxh42
echo "Loaded GROMACS"
command -v gmx

export OMP_NUM_THREADS=8

echo "Aligning trajectories..."

cd run-align
python3 align-mda.py > mda.log 2>&1 

echo "Aligned trajectories, now running hENM refinement"

cd ../run-fluc
bash commands.dat

# cd ../../lammps/lammps-input
# python3 get_data.py lammpsdata.dat
# python3 get_bond_coeff.py lammpsbondcoeff.dat

echo "Done"

deactivate

echo "Finished"
