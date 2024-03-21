#!/bin/sh
#PBS -l walltime=1:00:00
#PBS -N job_0_0
#PBS -l nodes=1:ppn=1
#PBS -M taolue.yang@temple.edu
#PBS -o /home/tus53997/Benchmark_DNACompression/logs/logs/job_0_0_output.log
#PBS -e /home/tus53997/Benchmark_DNACompression/logs/logs/job_0_0_error.log


cd $PBS_O_WORKDIR
module load singularity

#!/bin/bash
START_TIME=$SECONDS
singularity exec --bind /home/tus53997:/mnt /home/tus53997/sz3_perf_amd.sif /home/tus53997/Benchmark_DNACompression/ExternalDependencies/SZ3/bin/sz3 -a -f -M ABS 0.1 -2 152 420175 -i /home/tus53997/Benchmark_DNACompression/Scripts/../binFile/ERR103405_2_F.bin -o /home/tus53997/Benchmark_DNACompression/Scripts/../binFile/ERR103405_2_F.bin_-a_-f_-M_ABS_0.1_-2_152_420175.sz
END_TIME=$SECONDS
DURATION=$((END_TIME - START_TIME))

INPUT_SIZE=$(stat -c %s "/home/tus53997/Benchmark_DNACompression/Scripts/../binFile/ERR103405_2_F.bin")
OUTPUT_SIZE=$(stat -c %s "/home/tus53997/Benchmark_DNACompression/Scripts/../binFile/ERR103405_2_F.bin_-a_-f_-M_ABS_0.1_-2_152_420175.sz")
RATIO=$(echo "scale=2;  $INPUT_SIZE/$OUTPUT_SIZE" | bc)

echo "SZ3-a -f -M ABS 0.1 -2 152 420175,$DURATION,$RATIO" >> "/home/tus53997/Benchmark_DNACompression/logs/compression_metrics.csv"

