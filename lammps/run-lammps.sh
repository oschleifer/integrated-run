# source spack & load lammps
source /usr/workspace/mummiusr/mummi-spack/spack/0.21/share/spack/setup-env.sh
spack load lammps arch=$(spack arch)
command -v lmp

# source mummi
source ~/.mummi/config.mummi.sh
env | grep MUMMI

# original location of lammps input files: $MUMMI_RESOURCES/ucg

# create and run job
cd ucg
lalloc 2 -W 30
export OMP_NUM_THREADS=8
jsrun -n1 -c1 lmp -v seed 1 -in lammps.in &

# Each LAMMPS will write a trajectory file named ucg.traj.xyz
wait