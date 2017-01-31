#! /bin/bash 
# 
#SBATCH -J fit-candy      # job name
#SBATCH -o /scratch/network/jgreco/run-%j.out
#SBATCH -e /scratch/network/jgreco/run-%j.err             
#SBATCH -N 2
#SBATCH --ntasks-per-node=16
#SBATCH -t 1:00:00 
#SBATCH --mail-type=begin
#SBATCH --mail-type=end 
#SBATCH --mail-user=jgreco@princeton.edu 

cd /home/jgreco/projects/hugs/scripts/fits

RUNDIR=$HUGS_PIPE_IO/candy-cutouts/20170130-143629/

mpiexec -n 32 python batch_fit.py --mpi --path $RUNDIR
