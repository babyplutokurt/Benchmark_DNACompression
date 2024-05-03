#!/bin/sh
#PBS -l walltime=168:00:00
#PBS -N job_input1_3_0
#PBS -l nodes=1:ppn=12
#PBS -M taolue.yang@temple.edu
#PBS -o /home/tus53997/Benchmark_DNACompression/logs/logs/job_input1_3_0_output.log
#PBS -e /home/tus53997/Benchmark_DNACompression/logs/logs/job_input1_3_0_error.log




cd $PBS_O_WORKDIR
module load singularity

#!/bin/bash
START_TIME=$SECONDS
singularity exec --bind /home/tus53997:/mnt /home/tus53997/sz3_perf_amd.sif /home/tus53997/Benchmark_DNACompression/ExternalDependencies/Spring/build/spring -c -l -q ill_bin -i /home/tus53997/Benchmark_DNACompression/Scripts/../Fastq/HG00097_CCAAGTCT-AAGGATGA_HCLHLDSXX_L004_001.R2.fastq -o /home/tus53997/Benchmark_DNACompression/Scripts/../CompressedOutput/HG00097_CCAAGTCT-AAGGATGA_HCLHLDSXX_L004_001.R2.fastq_-c_-l_-q_ill_bin.spring
END_TIME=$SECONDS
DURATION=$((END_TIME - START_TIME))

# Differentiate the handling based on the compressor type
if [ "Other" == "SZ3" ]; then
    INPUT_SIZE=$(stat -c %s "/home/tus53997/Benchmark_DNACompression/Scripts/../Fastq/HG00097_CCAAGTCT-AAGGATGA_HCLHLDSXX_L004_001.R2.fastq")
    OUTPUT_SIZE=$(stat -c %s "/home/tus53997/Benchmark_DNACompression/Scripts/../CompressedOutput/HG00097_CCAAGTCT-AAGGATGA_HCLHLDSXX_L004_001.R2.fastq_-c_-l_-q_ill_bin.spring")
    ADJUSTED_INPUT_SIZE=$((INPUT_SIZE / 4))
    TOTAL_ORIGINAL_SIZE=$(echo "7398565080" | bc)
    TOTAL_COMPRESSED_SIZE=$(echo "1585450003" | bc)

    FINAL_ORIGINAL_SIZE=$(($ADJUSTED_INPUT_SIZE + $TOTAL_ORIGINAL_SIZE))
    FINAL_COMPRESSED_SIZE=$(($OUTPUT_SIZE + $TOTAL_COMPRESSED_SIZE))

    RATIO=$(echo "scale=2; $FINAL_ORIGINAL_SIZE / $FINAL_COMPRESSED_SIZE" | bc)
else
    INPUT_SIZE=$(stat -c %s "/home/tus53997/Benchmark_DNACompression/Scripts/../Fastq/HG00097_CCAAGTCT-AAGGATGA_HCLHLDSXX_L004_001.R2.fastq")
    OUTPUT_SIZE=$(stat -c %s "/home/tus53997/Benchmark_DNACompression/Scripts/../CompressedOutput/HG00097_CCAAGTCT-AAGGATGA_HCLHLDSXX_L004_001.R2.fastq_-c_-l_-q_ill_bin.spring")
    RATIO=$(echo "scale=2; $INPUT_SIZE / $OUTPUT_SIZE" | bc)
fi

echo "job_input1_3_0,spring-c -l -q ill_bin,$DURATION,$RATIO" >> "/home/tus53997/Benchmark_DNACompression/logs/compression_metrics1.csv"


source /home/tus53997/miniconda3/bin/activate compression

conda deactivate
