#!/bin/bash

#SBATCH --job-name=affa
#SBATCH --partition=grotthuss
#SBATCH --exclusive
#SBATCH --gres=gpu:2
#SBATCH --ntasks=12
#SBATCH --time=24:00:00

NPME=6
NPROC=12
GPU_ID=000111

module unload gromacs
module unload cuda
module unload intel
module unload intelmpi


module load gromacs/5.0-cuda+intelmpi-5.0+intel-15.0

mpirun -np 1 gmx_mpi grompp -f nvt.mdp -c ../1.min/min.gro -p ../../setup/output/topol.top -o nvt.tpr


mpirun -np $NPROC gmx_mpi mdrun -npme $NPME -v -deffnm nvt -gpu_id $GPU_ID 

cd ../3.npt
sbatch run.sh

