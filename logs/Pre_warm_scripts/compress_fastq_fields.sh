#!/bin/bash

# Extract the different fields from the FASTQ file
awk 'NR%4==1 {print > "/home/tus53997/Benchmark_DNACompression/Fastq/Individual_fields/base_identifiers.fastq"} NR%4==2 {print > "/home/tus53997/Benchmark_DNACompression/Fastq/Individual_fields/dna_bases.fastq"} NR%4==3 {print > "/home/tus53997/Benchmark_DNACompression/Fastq/Individual_fields/quality_identifiers.fastq"}' /home/tus53997/Benchmark_DNACompression/Scripts/.././Fastq/ERR103405_2.fastq

# Compress each field with zstd
zstd --ultra --long -f /home/tus53997/Benchmark_DNACompression/Fastq/Individual_fields/base_identifiers.fastq
zstd --ultra --long -f /home/tus53997/Benchmark_DNACompression/Fastq/Individual_fields/dna_bases.fastq
zstd --ultra --long -f /home/tus53997/Benchmark_DNACompression/Fastq/Individual_fields/quality_identifiers.fastq
