#!/bin/sh
#PBS -l walltime=1:00:00
#PBS -N job_7_1
#PBS -l nodes=1:ppn=4
#PBS -M taolue.yang@temple.edu
#PBS -o /home/tus53997/Benchmark_DNACompression/logs/logs/job_7_1_output.log
#PBS -e /home/tus53997/Benchmark_DNACompression/logs/logs/job_7_1_error.log
#PBS -W depend=afterok:70132



cd $PBS_O_WORKDIR
module load singularity
singularity exec --bind /home/tus53997:/mnt /home/tus53997/sz3_perf_amd.sif /home/tus53997/Benchmark_DNACompression/ExternalDependencies/fqzcomp/fqzcomp -d /home/tus53997/Benchmark_DNACompression/Scripts/../CompressedOutput/ERR103405_2.fastq_-Q_5.fqz /home/tus53997/Benchmark_DNACompression/Scripts/../DecompressedOutput/ERR103405_2.fastq_-Q_5_decompressed.fastq

source /home/tus53997/miniconda3/bin/activate compression

conda deactivate
