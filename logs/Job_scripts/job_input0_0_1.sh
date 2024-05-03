#!/bin/sh
#PBS -l walltime=168:00:00
#PBS -N job_input0_0_1
#PBS -l nodes=1:ppn=12
#PBS -M taolue.yang@temple.edu
#PBS -o /home/tus53997/Benchmark_DNACompression/logs/logs/job_input0_0_1_output.log
#PBS -e /home/tus53997/Benchmark_DNACompression/logs/logs/job_input0_0_1_error.log


cd $PBS_O_WORKDIR
module load singularity
singularity exec --bind /home/tus53997:/mnt /home/tus53997/sz3_perf_amd.sif /home/tus53997/Benchmark_DNACompression/ExternalDependencies/SZ3/bin/sz3 -f -1 5126799450 -M REL 0.8 -z /home/tus53997/Benchmark_DNACompression/Scripts/../CompressedOutput/HG00097_CCAAGTCT-AAGGATGA_HCLHLDSXX_L004_001.R1.bin_-f_-1_5126799450_-M_REL_0.8.sz -o /home/tus53997/Benchmark_DNACompression/Scripts/../DecompressedOutput/HG00097_CCAAGTCT-AAGGATGA_HCLHLDSXX_L004_001.R1.bin_-f_-1_5126799450_-M_REL_0.8_decompressed.sz.out

source /home/tus53997/miniconda3/bin/activate compression

python -c "import sys; sys.path.append('/home/tus53997/Benchmark_DNACompression/Scripts'); from SZ3_Decompress_Assembler import reconstruct_fastq; reconstruct_fastq('/home/tus53997/Benchmark_DNACompression/Fastq/Individual_fields/dna_bases0.fastq',
        '/home/tus53997/Benchmark_DNACompression/Fastq/Individual_fields/base_identifiers0.fastq',
        '/home/tus53997/Benchmark_DNACompression/Fastq/Individual_fields/quality_identifiers0.fastq',
        '/home/tus53997/Benchmark_DNACompression/CompressedOutput/../DecompressedOutput/HG00097_CCAAGTCT-AAGGATGA_HCLHLDSXX_L004_001.R1.bin_-f_-1_5126799450_-M_REL_0.8_decompressed.sz.out',
        '/home/tus53997/Benchmark_DNACompression/CompressedOutput/../DecompressedOutput/HG00097_CCAAGTCT-AAGGATGA_HCLHLDSXX_L004_001.R1.bin_-f_-1_5126799450_-M_REL_0.8_decompressed.sz.out.fastq',
        max_quality_char='F')"

conda deactivate
