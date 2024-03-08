#!/bin/sh
#PBS -l walltime=1:00:00
#PBS -N sz3_job
#PBS -l nodes=1:ppn=1
#PBS -M taolue.yang@temple.edu
#PBS -m abe
#PBS -o /home/tus53997/Benchmark_DNACompression/jobs/sz3_job_output.log
#PBS -e /home/tus53997/Benchmark_DNACompression/jobs/sz3_job_error.log

# Change to directory where 'qsub' was called
cd $PBS_O_WORKDIR

# Load the singularity module
module load singularity
singularity exec --bind /home/tus53997:/mnt sz3_perf_amd.sif /home/tus53997/Benchmark_DNACompression/ExternalDependencies/SZ3/bin/sz3 -a -i /home/tus53997/Benchmark_DNACompression/binFile/ERR103405_2_F.bin -o /home/tus53997/Benchmark_DNACompression/binFile/ERR103405_2_F.bin.sz -f -M ABS 0.1 -2 152 420175 
