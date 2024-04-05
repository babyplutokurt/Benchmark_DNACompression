import re
import csv
import json
import os
from Fastq_sizeChecker import analyze_fastq

Bench_path = ''
identifier_bytes, bases_bytes, quality_bytes = analyze_fastq(
    "/home/tus53997/Benchmark_DNACompression/Fastq/ERR103405_2.fastq")


def parse_sz3_log(log_file_path, log_error_path, _identifier_bytes=identifier_bytes, _bases_bytes=bases_bytes,
                  _quality_bytes=quality_bytes):
    current_working_directory = os.getcwd()
    size_metrics_json = current_working_directory + '/../logs/size_metrics.json'

    with open(size_metrics_json, 'r') as file:
        size_metrics = json.load(file)

    # Define patterns to match the required information
    compression_ratio_pattern = re.compile(r'compression ratio = ([\d.]+)')
    compression_time_pattern = re.compile(r'compression time = ([\d.]+)')

    metrics = {
        'Quality Score Compression Ratio': 0,  # Since we're interested in the quality score compression ratio
        'Compression_time_seconds': 0,
        'Base Compression Ratio': 0,
        'Identifier Compression ratio': 0
    }

    # Open and read the log file
    with open(log_file_path, 'r') as file:
        for line in file:
            if compression_ratio_match := compression_ratio_pattern.search(line):
                # Note: The requirement to divide the compression ratio by 4
                metrics['Quality Score Compression Ratio'] = float(compression_ratio_match.group(1)) / 4
            elif compression_time_match := compression_time_pattern.search(line):
                metrics['Compression_time_seconds'] = float(compression_time_match.group(1))

    metrics['Base Compression Ratio'] = size_metrics['dna_bases.fastq']['original_size'] / \
                                        size_metrics['dna_bases.fastq']['compressed_size']
    metrics['Identifier Compression ratio'] = size_metrics['base_identifiers.fastq']['original_size'] * 2 / \
                                              size_metrics['base_identifiers.fastq']['compressed_size']

    return metrics


def parse_fqzcomp_log(log_file_path, log_error_path, _identifier_bytes=identifier_bytes, _bases_bytes=bases_bytes,
                      _quality_bytes=quality_bytes):
    # Define patterns to match the required information
    names_pattern = re.compile(r'Names\s+(\d+)\s+->\s+(\d+)\s+\(([\d.]+)\)')
    bases_pattern = re.compile(r'Bases\s+(\d+)\s+->\s+(\d+)\s+\(([\d.]+)\)')
    quals_pattern = re.compile(r'Quals\s+(\d+)\s+->\s+(\d+)\s+\(([\d.]+)\)')

    # Initialize dictionary to hold the extracted values
    metrics = {
        'Names_original': 0,
        'Names_compressed': 0,
        'Identifier Compression ratio': 0,
        'Bases_original': 0,
        'Bases_compressed': 0,
        'Base Compression Ratio': 0,
        'Quals_original': 0,
        'Quals_compressed': 0,
        'Quality Score Compression Ratio': 0,
    }

    # Open and read the log file
    with open(log_error_path, 'r') as file:
        for line in file:
            if names_match := names_pattern.search(line):
                metrics['Names_original'] = int(names_match.group(1))
                metrics['Names_compressed'] = int(names_match.group(2))
                metrics['Identifier Compression ratio'] = metrics['Names_original']/metrics['Names_compressed']
            elif bases_match := bases_pattern.search(line):
                metrics['Bases_original'] = int(bases_match.group(1))
                metrics['Bases_compressed'] = int(bases_match.group(2))
                metrics['Base Compression Ratio'] = metrics['Bases_original']/metrics['Bases_compressed']
            elif quals_match := quals_pattern.search(line):
                metrics['Quals_original'] = int(quals_match.group(1))
                metrics['Quals_compressed'] = int(quals_match.group(2))
                metrics['Quality Score Compression Ratio'] = metrics['Quals_original']/metrics['Quals_compressed']

    return metrics


def parse_spring_log(log_file_path, log_error_path, _identifier_bytes=identifier_bytes, _bases_bytes=bases_bytes,
                     _quality_bytes=quality_bytes):
    # Define patterns to match the required information
    reads_pattern = re.compile(r'Reads:\s+(\d+) bytes')
    quality_pattern = re.compile(r'Quality:\s+(\d+) bytes')
    id_pattern = re.compile(r'ID:\s+(\d+) bytes')
    total_size_pattern = re.compile(r'Total size:\s+(\d+) bytes')
    total_time_pattern = re.compile(r'Total time for compression: (\d+) s')

    # Initialize dictionary to hold the extracted values
    metrics = {
        'Reads_bytes': 0,
        'Quality_bytes': 0,
        'ID_bytes': 0,
        'Total_size_bytes': 0,
        'Total_time_seconds': 0,
    }

    # Open and read the log file
    with open(log_file_path, 'r') as file:
        for line in file:
            if reads_match := reads_pattern.search(line):
                metrics['Reads_bytes'] = int(reads_match.group(1))
            elif quality_match := quality_pattern.search(line):
                metrics['Quality_bytes'] = int(quality_match.group(1))
            elif id_match := id_pattern.search(line):
                metrics['ID_bytes'] = int(id_match.group(1))
            elif total_size_match := total_size_pattern.search(line):
                metrics['Total_size_bytes'] = int(total_size_match.group(1))
            elif total_time_match := total_time_pattern.search(line):
                metrics['Total_time_seconds'] = int(total_time_match.group(1))
    metrics['Identifier Compression ratio'] = identifier_bytes / metrics['ID_bytes']
    metrics['Base Compression Ratio'] = bases_bytes / metrics['Reads_bytes']
    metrics['Quality Score Compression Ratio'] = quality_bytes / metrics['Quality_bytes']
    return metrics


if __name__ == "__main__":
    print(parse_sz3_log('/home/tus53997/Benchmark_DNACompression/logs/logs/job_0_0_output.log',
                        '/home/tus53997/Benchmark_DNACompression/logs/logs/job_1_0_error.log'))
