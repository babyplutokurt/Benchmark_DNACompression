#!/bin/sh
#PBS -l walltime=1:00:00
#PBS -N job_1_0
#PBS -l nodes=1:ppn=1
#PBS -M taolue.yang@temple.edu
#PBS -o /home/tus53997/Benchmark_DNACompression/logs/logs/job_1_0_output.log
#PBS -e /home/tus53997/Benchmark_DNACompression/logs/logs/job_1_0_error.log


cd $PBS_O_WORKDIR
module load singularity

#!/bin/bash
START_TIME=$SECONDS
singularity exec --bind /home/tus53997:/mnt /home/tus53997/sz3_perf_amd.sif /home/tus53997/Benchmark_DNACompression/ExternalDependencies/SZ3/bin/sz3 -a -f -M ABS 0.1 -1 63866600 -i /home/tus53997/Benchmark_DNACompression/Scripts/../binFile/ERR103405_2_F.bin -o /home/tus53997/Benchmark_DNACompression/Scripts/../binFile/ERR103405_2_F.bin_-a_-f_-M_ABS_0.1_-1_63866600.sz
END_TIME=$SECONDS
DURATION=$((END_TIME - START_TIME))

INPUT_SIZE=$(stat -c %s "/home/tus53997/Benchmark_DNACompression/Scripts/../binFile/ERR103405_2_F.bin")
OUTPUT_SIZE=$(stat -c %s "/home/tus53997/Benchmark_DNACompression/Scripts/../binFile/ERR103405_2_F.bin_-a_-f_-M_ABS_0.1_-1_63866600.sz")
RATIO=$(echo "scale=2;  $INPUT_SIZE/$OUTPUT_SIZE" | bc)

echo "SZ3-a -f -M ABS 0.1 -1 63866600,$DURATION,$RATIO" >> "/home/tus53997/Benchmark_DNACompression/logs/compression_metrics.csv"

