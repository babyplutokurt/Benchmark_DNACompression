import numpy as np
import pandas as pd
import csv
from Fastq_ratioCheker import parse_sz3_log, parse_fqzcomp_log, parse_spring_log


def generate_paths_and_compressor(csv_file_path):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)
    # Base directory for log files (adjust as necessary)
    log_base_dir = "/home/tus53997/Benchmark_DNACompression/logs/logs"
    parse_info = []
    for index, row in df.iterrows():
        job_id = row['job_id']
        compressor_name = row['Compressor Name'].split()[0].lower()  # Taking the first word and making it lowercase
        if compressor_name.startswith("sz3"):
            compressor = "sz3"
        elif compressor_name.startswith("fqzcomp"):
            compressor = "fqzcomp"
        elif compressor_name.startswith("spring"):
            compressor = "spring"
        else:
            compressor = "unknown"
        output_log_path = f"{log_base_dir}/{job_id}_output.log"
        error_log_path = f"{log_base_dir}/{job_id}_error.log"
        parse_info.append([job_id, output_log_path, error_log_path, compressor])
    return parse_info


def parser_csv(filename='/home/tus53997/Benchmark_DNACompression/Analysis/ratio.csv'):
    header = ['job_id', 'Base Compression Ratio', 'Quality Score Compression Ratio', 'Identifier Compression ratio']
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)

    columns = []
    csv_file_path = '/home/tus53997/Benchmark_DNACompression/logs/compression_metrics.csv'
    parse_info = generate_paths_and_compressor(csv_file_path)
    for job_id, output_log_path, error_log_path, compressor in parse_info:
        temp_row = {'job_id': job_id, 'Base Compression Ratio': np.nan, 'Quality Score Compression Ratio': np.nan,
                    'Identifier Compression ratio': np.nan}
        if compressor == 'sz3':
            metric = parse_sz3_log(output_log_path, error_log_path)
            for key in temp_row:
                if key in metric:
                    temp_row[key] = metric[key]
            print(temp_row)
            columns.append(temp_row)
        elif compressor == 'fqzcomp':
            metric = parse_fqzcomp_log(output_log_path, error_log_path)
            for key in temp_row:
                if key in metric:
                    temp_row[key] = metric[key]
            print(temp_row)
            columns.append(temp_row)
        elif compressor == 'spring':
            metric = parse_spring_log(output_log_path, error_log_path)
            for key in temp_row:
                if key in metric:
                    temp_row[key] = metric[key]
            print(temp_row)
            columns.append(temp_row)
    df = pd.DataFrame(columns)
    df.to_csv(filename, index=False)
    print("CSV file has been written successfully.")


if __name__ == "__main__":
    parser_csv()