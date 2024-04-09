#!/bin/sh
#PBS -l walltime=1:00:00
#PBS -N job_0_0
#PBS -l nodes=1:ppn=4
#PBS -M taolue.yang@temple.edu
#PBS -o /home/tus53997/Benchmark_DNACompression/logs/logs/job_0_0_output.log
#PBS -e /home/tus53997/Benchmark_DNACompression/logs/logs/job_0_0_error.log




cd $PBS_O_WORKDIR
module load singularity

#!/bin/bash
START_TIME=$SECONDS
singularity exec --bind /home/tus53997:/mnt /home/tus53997/sz3_perf_amd.sif /home/tus53997/Benchmark_DNACompression/ExternalDependencies/SZ3/bin/sz3 -f -1 63866600 -M ABS 0.1 -i /home/tus53997/Benchmark_DNACompression/Scripts/../binFile/ERR103405_2_F.bin -z /home/tus53997/Benchmark_DNACompression/Scripts/../CompressedOutput/ERR103405_2_F.bin_-f_-1_63866600_-M_ABS_0.1.sz
END_TIME=$SECONDS
DURATION=$((END_TIME - START_TIME))

# Differentiate the handling based on the compressor type
if [ "SZ3" == "SZ3" ]; then
    INPUT_SIZE=$(stat -c %s "/home/tus53997/Benchmark_DNACompression/Scripts/../binFile/ERR103405_2_F.bin")
    OUTPUT_SIZE=$(stat -c %s "/home/tus53997/Benchmark_DNACompression/Scripts/../CompressedOutput/ERR103405_2_F.bin_-f_-1_63866600_-M_ABS_0.1.sz")
    ADJUSTED_INPUT_SIZE=$((INPUT_SIZE / 4))
    TOTAL_ORIGINAL_SIZE=$(echo "108421061" | bc)
    TOTAL_COMPRESSED_SIZE=$(echo "17590814" | bc)
    
    FINAL_ORIGINAL_SIZE=$(($ADJUSTED_INPUT_SIZE + $TOTAL_ORIGINAL_SIZE))
    FINAL_COMPRESSED_SIZE=$(($OUTPUT_SIZE + $TOTAL_COMPRESSED_SIZE))
    
    RATIO=$(echo "scale=2; $FINAL_ORIGINAL_SIZE / $FINAL_COMPRESSED_SIZE" | bc)
else
    INPUT_SIZE=$(stat -c %s "/home/tus53997/Benchmark_DNACompression/Scripts/../binFile/ERR103405_2_F.bin")
    OUTPUT_SIZE=$(stat -c %s "/home/tus53997/Benchmark_DNACompression/Scripts/../CompressedOutput/ERR103405_2_F.bin_-f_-1_63866600_-M_ABS_0.1.sz")
    RATIO=$(echo "scale=2; $INPUT_SIZE / $OUTPUT_SIZE" | bc)
fi

echo "job_0_0,SZ3-f -1 63866600 -M ABS 0.1,$DURATION,$RATIO" >> "/home/tus53997/Benchmark_DNACompression/logs/compression_metrics.csv"


source /home/tus53997/miniconda3/bin/activate compression

conda deactivate
