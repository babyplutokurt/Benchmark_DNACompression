#!/bin/sh
#PBS -l walltime=1:00:00
#PBS -N Size_cheker
#PBS -l nodes=1:ppn=24
#PBS -M taolue.yang@temple.edu
#PBS -o /home/tus53997/Benchmark_DNACompression/Temp_test/Size_cheker_output.log
#PBS -e /home/tus53997/Benchmark_DNACompression/Temp_test/Size_cheker_error.log

cd $PBS_O_WORKDIR

source /home/tus53997/miniconda3/bin/activate compression

python /home/tus53997/Benchmark_DNACompression/Analysis/QualityConverter.py

conda deactivate