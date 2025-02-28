
##########################
##### Run GROMACS :) #####
##########################

# TODO: change per user
cDir="/p/gpfs1/ipe1/integration"
cd $cDir

# bash ../run_four_gmx_jobs.sh
# Simulation subdirectories -- rename them based on your folders
sim1Dir = "sim_1"
sim2Dir = "sim_2"
sim3Dir = "sim_3"
sim4Dir = "sim_4"
bsub -nnodes 1 -W 60 -G cancer -q pbatch ${cDir}/run_gmx.sh 1 ${cDir}/${sim1Dir} ${cDir}/${sim2Dir} ${cDir}/${sim3Dir} ${cDir}/${sim4Dir}

# this makes x1 node job (running x4 simulations) runs for 12h and x3 chained dependent jobs to start after the previous finishes (note gmx mdrun -cpi flag makes gromacs restart from last checkpoint file).

##########################
##### (: Run hENM :) #####
##########################

cd henm 
# consider what input/output and location
# GROMACS trajectory files will be in each simulation's subdirectory
bash run-henm.sh

##########################
##### Run LAMMPS :) ######
##########################

cd lammps

bash run-lammps.sh