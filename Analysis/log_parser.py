import json

import numpy as np
import pandas as pd
import csv
import os
from Fastq_ratioCheker import parse_sz3_log, parse_fqzcomp_log, parse_spring_log


def generate_paths_and_compressor(csv_file_path):
    df = pd.read_csv(csv_file_path)
    log_base_dir = "/home/tus53997/Benchmark_DNACompression/logs/logs"
    parse_info = []
    for index, row in df.iterrows():
        job_id = row['job_id']
        compressor_name = row['Compressor Name'].split()[0].lower()
        compressor = 'unknown'
        if compressor_name.startswith("sz3"):
            compressor = "sz3"
        elif compressor_name.startswith("fqzcomp"):
            compressor = "fqzcomp"
        elif compressor_name.startswith("spring"):
            compressor = "spring"
        output_log_path = os.path.join(log_base_dir, f"{job_id}_output.log")
        error_log_path = os.path.join(log_base_dir, f"{job_id}_error.log")
        parse_info.append([job_id, output_log_path, error_log_path, compressor])
    return parse_info


def parser_csv(input_file_name, metrics_csv_path, output_dir):
    filename = f'ratio_{os.path.basename(input_file_name)}.csv'
    output_path = os.path.join(output_dir, filename)
    header = ['job_id', 'Base Compression Ratio', 'Quality Score Compression Ratio', 'Identifier Compression ratio']

    columns = []
    parse_info = generate_paths_and_compressor(metrics_csv_path)
    for job_id, output_log_path, error_log_path, compressor in parse_info:
        temp_row = {'job_id': job_id, 'Base Compression Ratio': np.nan, 'Quality Score Compression Ratio': np.nan,
                    'Identifier Compression ratio': np.nan}
        if compressor != 'unknown':
            metric = globals()[f'parse_{compressor}_log'](output_log_path, error_log_path)
            temp_row.update(metric)
            columns.append(temp_row)

    df = pd.DataFrame(columns)
    df.to_csv(output_path, index=False)
    print(f"CSV file has been written successfully to {output_path}")


if __name__ == "__main__":
    config_path = '/home/tus53997/Benchmark_DNACompression/jobs/bench.json'
    output_dir = '/home/tus53997/Benchmark_DNACompression/Analysis'

    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
        input_files = config["input_file"]

    for input_file in input_files:
        metrics_csv_path = f'/home/tus53997/Benchmark_DNACompression/logs/compression_metrics_{os.path.basename(input_file)}.csv'
        parser_csv(input_file, metrics_csv_path, output_dir)
