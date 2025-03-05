#!/usr/bin/env bash

if [ "$#" -ne 5 ]; then
  echo "Illegal number of parameters"
  echo "usage: $0 max_hours sim_dir1 sim_dir2 sim_dir3 sim_dir4"
  exit
fi


#source /usr/workspace/mummiusr/mummi-spack/spack/0.19/share/spack/setup-env.sh
#export MUMMI_SPACK_TARGET=$(spack arch --target)
#spack load flux-sched target=$MUMMI_SPACK_TARGET
#spack load gromacs@2022.06.gpu target=$MUMMI_SPACK_TARGET
source /usr/WS1/mummiusr/mummi-spack-temp/spack/0.21/share/spack/setup-env.sh
spack load flux-sched
#spack load gromacs@2023.4.gpu+cuda
spack load gromacs@2024.1.gpu

export OMP_NUM_THREADS=10
NB_NODES=1 # Number of nodes used to bootstrap Flux

CMD="flux mini run -N 1 -n 1 -c 10 -g 1 -o mpi=spectrum -o cpu-affinity=per-task -o gpu-affinity=per-task"

TS=$(date "+%Y%m%d-%H%M%S-%3N")
${PWD}/bootstrap_flux.sh ${NB_NODES} ${TS}

export FLUX_URI=$(cat mummi-uri-${TS}.log)
FLUX_PID=$(cat mummi-flux-pid-${TS}.log)

MDLOG=mdrun.log

echo "Run gromacs GPU for $1 hours:"
echo "scheduler command: $CMD"
echo "   $2"
echo "   $3"
echo "   $4"
echo "   $5"

cd $2
echo "Run $2"
pwd
$CMD gmx mdrun -cpi -nb gpu -ntmpi 1 -ntomp $OMP_NUM_THREADS -pin off -maxh $1 >> ${MDLOG} 2>&1 &
echo "" > cg_running
cd ../

cd $3
echo "Run $3"
pwd
$CMD gmx mdrun -cpi -nb gpu -ntmpi 1 -ntomp $OMP_NUM_THREADS -pin off -maxh $1 >> ${MDLOG} 2>&1 &
echo "" > cg_running
cd ../

cd $4
echo "Run $4"
pwd
$CMD gmx mdrun -cpi -nb gpu -ntmpi 1 -ntomp $OMP_NUM_THREADS -pin off -maxh $1 >> ${MDLOG} 2>&1 &
echo "" > cg_running
cd ../

cd $5
echo "Run $5"
pwd
$CMD gmx mdrun -cpi -nb gpu -ntmpi 1 -ntomp $OMP_NUM_THREADS -pin off -maxh $1 >> ${MDLOG} 2>&1 &
echo "" > cg_running
cd ../

wait
echo "All sims done"
echo "Killing Flux"
kill $FLUX_PID
