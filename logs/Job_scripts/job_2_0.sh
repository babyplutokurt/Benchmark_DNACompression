#!/bin/sh
#PBS -l walltime=1:00:00
#PBS -N job_2_0
#PBS -l nodes=1:ppn=1
#PBS -M taolue.yang@temple.edu
#PBS -o /home/tus53997/Benchmark_DNACompression/logs/logs/job_2_0_output.log
#PBS -e /home/tus53997/Benchmark_DNACompression/logs/logs/job_2_0_error.log


cd $PBS_O_WORKDIR
module load singularity

#!/bin/bash
START_TIME=$SECONDS
singularity exec --bind /home/tus53997:/mnt /home/tus53997/sz3_perf_amd.sif /home/tus53997/Benchmark_DNACompression/ExternalDependencies/Spring/build/spring -c -l -q qvz 0.6 -i /home/tus53997/Benchmark_DNACompression/Scripts/../Fastq/ERR103405_2.fastq -o /home/tus53997/Benchmark_DNACompression/Scripts/../CompressedOutput/ERR103405_2.fastq_-c_-l_-q_qvz_0.6.spring
END_TIME=$SECONDS
DURATION=$((END_TIME - START_TIME))

INPUT_SIZE=$(stat -c %s "/home/tus53997/Benchmark_DNACompression/Scripts/../Fastq/ERR103405_2.fastq")
OUTPUT_SIZE=$(stat -c %s "/home/tus53997/Benchmark_DNACompression/Scripts/../CompressedOutput/ERR103405_2.fastq_-c_-l_-q_qvz_0.6.spring")
RATIO=$(echo "scale=2;  $INPUT_SIZE/$OUTPUT_SIZE" | bc)

echo "job_2_0, spring-c -l -q qvz 0.6,$DURATION,$RATIO" >> "/home/tus53997/Benchmark_DNACompression/logs/compression_metrics.csv"

