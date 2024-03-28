#!/bin/sh
#PBS -l walltime=1:00:00
#PBS -N job_8_1
#PBS -l nodes=1:ppn=1
#PBS -M taolue.yang@temple.edu
#PBS -o /home/tus53997/Benchmark_DNACompression/logs/logs/job_8_1_output.log
#PBS -e /home/tus53997/Benchmark_DNACompression/logs/logs/job_8_1_error.log
#PBS -W depend=afterok:69656

cd $PBS_O_WORKDIR
module load singularity
singularity exec --bind /home/tus53997:/mnt /home/tus53997/sz3_perf_amd.sif /home/tus53997/Benchmark_DNACompression/ExternalDependencies/SZ3/bin/sz3 -f -1 63866600 -M REL 0.2 -z /home/tus53997/Benchmark_DNACompression/Scripts/../CompressedOutput/ERR103405_2_F.bin_-f_-1_63866600_-M_REL_0.2.sz -o /home/tus53997/Benchmark_DNACompression/Scripts/../DecompressedOutput/ERR103405_2_F.bin_-f_-1_63866600_-M_REL_0.2_decompressed.sz.out