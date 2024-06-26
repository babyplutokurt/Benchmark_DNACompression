#!/bin/sh
#PBS -l walltime=168:00:00
#PBS -N job_input0_1_1
#PBS -l nodes=1:ppn=12
#PBS -M taolue.yang@temple.edu
#PBS -o /home/tus53997/Benchmark_DNACompression/logs/logs/job_input0_1_1_output.log
#PBS -e /home/tus53997/Benchmark_DNACompression/logs/logs/job_input0_1_1_error.log
#PBS -W depend=afterok:70934



cd $PBS_O_WORKDIR
module load singularity
singularity exec --bind /home/tus53997:/mnt /home/tus53997/sz3_perf_amd.sif /home/tus53997/Benchmark_DNACompression/ExternalDependencies/fqzcomp/fqzcomp -d /home/tus53997/Benchmark_DNACompression/Scripts/../CompressedOutput/HG00097_CCAAGTCT-AAGGATGA_HCLHLDSXX_L004_001.R1.fastq_-Q_5.fqz /home/tus53997/Benchmark_DNACompression/Scripts/../DecompressedOutput/HG00097_CCAAGTCT-AAGGATGA_HCLHLDSXX_L004_001.R1.fastq_-Q_5_decompressed.fastq

source /home/tus53997/miniconda3/bin/activate compression

conda deactivate
