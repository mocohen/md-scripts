#!/bin/bash

#SBATCH --job-name=affa
#SBATCH --partition=gavothgpu
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

mpirun -np 1 gmx_mpi grompp -f npt_cont.mdp -c ../2.nvt/nvt.gro -p ../../setup/output/topol.top -o npt.tpr


mpirun -np $NPROC gmx_mpi mdrun -npme $NPME -v -deffnm npt -gpu_id $GPU_ID 

