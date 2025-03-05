
##########################
##### Run GROMACS :) #####
##########################

# TODO: change per user
# cDir="/p/gpfs1/ipe1/integration"
# cd $cDir
cDir="gromacs"

# bash ../run_four_gmx_jobs.sh
# Simulation subdirectories -- rename them based on your folders
sim1Dir = "sim_1"
sim2Dir = "sim_2"
sim3Dir = "sim_3"
sim4Dir = "sim_4"

# Runs 4 simulations of GROMACS
## Calls the run_gmx script
## Outputs into the simulation folders
bsub -nnodes 1 -W 60 -G cancer -q pbatch ${cDir}/run_gmx.sh 1 ${cDir}/${sim1Dir} ${cDir}/${sim2Dir} ${cDir}/${sim3Dir} ${cDir}/${sim4Dir}

# this makes x1 node job (running x4 simulations) runs for 1h

##########################
##### (: Run hENM :) #####
##########################

cd henm 
# consider what input/output and location
# GROMACS trajectory files will be in each simulation's subdirectory

# Runs henm script
bash run-henm.sh

##########################
##### Run LAMMPS :) ######
##########################

cd ../lammps

# Runs the LAMMPS script
bash run-lammps.sh