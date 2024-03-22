#!/bin/bash
#PBS -N analysis_job
#PBS -l walltime=01:00:00
#PBS -l select=1:ncpus=1:mem=128gb
#PBS -j oe
#PBS -o /home/tus53997/Benchmark_DNACompression/logs/analysis_job_output.log

source /home/tus53997/miniconda3/bin/activate compression


cd /home/tus53997/Benchmark_DNACompression/Analysis
# Run the analysis Python script
python3 /home/tus53997/Benchmark_DNACompression/Analysis/Metric_analysis.py

# Deactivate conda environment
conda deactivate
