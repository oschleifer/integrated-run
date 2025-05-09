
##########################
##### Run GROMACS :) #####
##########################

cDir="gromacs"

# Simulation subdirectories -- rename them based on your folders
sim1Dir="sim_1"
sim2Dir="sim_2"
sim3Dir="sim_3"
sim4Dir="sim_4"

# Runs 4 simulations of GROMACS
## Calls the run_gmx script
## Outputs into the simulation folders
bsub -nnodes 1 -W 60 -G cancer -q pbatch ${cDir}/run_gmx.sh 1 ${cDir}/${sim1Dir} ${cDir}/${sim2Dir} ${cDir}/${sim3Dir} ${cDir}/${sim4Dir}


##########################
##### (: Run hENM :) #####
##########################

source ~/.mummi/config.mummi.sh
source $MUMMI_APP/setup/setup.env.sh
spack load /nxpxh42
pip install .

python -m henm.pipeline \
    --inputs gromacs/sim_1/confout.gro gromacs/sim_1/traj_comp.xtc \
             gromacs/sim_2/confout.gro gromacs/sim_2/traj_comp.xtc \
             gromacs/sim_3/confout.gro gromacs/sim_3/traj_comp.xtc \
             gromacs/sim_4/confout.gro gromacs/sim_4/traj_comp.xtc \
    --out output/
   --lammps lammps/

##########################
##### Run LAMMPS :) ######
##########################

cd ../lammps

# Runs LAMMPS simulations 
bash run-lammps.sh
