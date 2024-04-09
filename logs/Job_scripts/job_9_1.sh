#!/bin/sh
#PBS -l walltime=1:00:00
#PBS -N job_9_1
#PBS -l nodes=1:ppn=4
#PBS -M taolue.yang@temple.edu
#PBS -o /home/tus53997/Benchmark_DNACompression/logs/logs/job_9_1_output.log
#PBS -e /home/tus53997/Benchmark_DNACompression/logs/logs/job_9_1_error.log
#PBS -W depend=afterok:70136



cd $PBS_O_WORKDIR
module load singularity
singularity exec --bind /home/tus53997:/mnt /home/tus53997/sz3_perf_amd.sif /home/tus53997/Benchmark_DNACompression/ExternalDependencies/Spring/build/spring -d -i /home/tus53997/Benchmark_DNACompression/Scripts/../CompressedOutput/ERR103405_2.fastq_-c_-l_-q_qvz_0.8.spring -o /home/tus53997/Benchmark_DNACompression/Scripts/../DecompressedOutput/ERR103405_2.fastq_-c_-l_-q_qvz_0.8_decompressed.fastq

source /home/tus53997/miniconda3/bin/activate compression

conda deactivate
