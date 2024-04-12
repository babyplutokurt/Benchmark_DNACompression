#!/bin/bash

# Extract the different fields from the FASTQ file
awk 'NR%4==1 {print > "/home/tus53997/Benchmark_DNACompression/Fastq/Individual_fields/base_identifiers0.fastq"} NR%4==2 {print > "/home/tus53997/Benchmark_DNACompression/Fastq/Individual_fields/dna_bases0.fastq"} NR%4==3 {print > "/home/tus53997/Benchmark_DNACompression/Fastq/Individual_fields/quality_identifiers0.fastq"}' /home/tus53997/Benchmark_DNACompression/Scripts/.././Fastq/ERR103405_2.fastq

# Compress each field with zstd
zstd --ultra --long -f /home/tus53997/Benchmark_DNACompression/Fastq/Individual_fields/base_identifiers0.fastq
zstd --ultra --long -f /home/tus53997/Benchmark_DNACompression/Fastq/Individual_fields/dna_bases0.fastq
zstd --ultra --long -f /home/tus53997/Benchmark_DNACompression/Fastq/Individual_fields/quality_identifiers0.fastq
