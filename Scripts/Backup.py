import subprocess
import os
import pandas as pd
import json
from QualityConverter import QualityConverter  # Assuming the class you've shared is saved as QualityConverter.py
from log_parser import parser_csv


def load_benchmark_info(bench_file_path):
    with open(bench_file_path, 'r') as file:
        data = json.load(file)
    return data


def determine_loader_method(job_name):
    if job_name.lower() in ['sz3']:  # Assuming binary output for these compressors
        return "decompress_loader"
    elif job_name.lower() in ['fqzcomp', 'spring']:  # Assuming FASTQ output for this compressor
        return "fastq_loader"
    else:
        return "unknown_loader"


def get_decompressed_output_path(project_root, job, input_file, binary_input_file_path):
    """
    Simplified logic to determine the decompressed output path based on job configuration.
    Adjust this logic based on how your CommandGenerator classes construct file paths.
    """
    output_path = ""
    if job['name'].upper() == "SZ3":
        if len(job['options']) == 2:
            first_option_full = job['options'][0].replace(" ", "_")
            input_file_path = os.path.join(project_root, binary_input_file_path)
            output_file_name = f"{os.path.basename(input_file_path)}_{first_option_full}.sz"
            output_file_name = os.path.basename(output_file_name).replace('.sz', '_decompressed.sz.out')
            output_path = os.path.join(project_root, 'DecompressedOutput', output_file_name)
    elif job['name'].upper() == "FQZCOMP":
        input_file_path = os.path.join(project_root, input_file)
        first_option_full = job['options'][0].replace(" ", "_")
        output_file_name = f"{os.path.basename(input_file_path)}_{first_option_full}.fqz"
        output_file_name = os.path.basename(output_file_name).replace('.fqz', '_decompressed.fastq')
        output_path = os.path.join(project_root, 'DecompressedOutput', output_file_name)
    elif job['name'].upper() == "SPRING":
        input_file_path = os.path.join(project_root, input_file)
        first_option_full = job['options'][0].replace(" ", "_")
        output_file_name = f"{os.path.basename(input_file_path)}_{first_option_full}.spring"
        output_file_name = os.path.basename(output_file_name).replace('.spring', '_decompressed.fastq')
        output_path = os.path.join(project_root, 'DecompressedOutput', output_file_name)
    else:
        raise ValueError(f"Unknown job type: {job['name']}")
    # decompressed_output_path = os.path.join(project_root, 'DecompressedOutput', output_file_name)
    print("Compressor: ", job['name'])
    print("output_path: ",
          output_path if output_path else "This job will be skipped in analysis, because it's not a Compression-Decompression workflow")
    return output_path


def metric_analysis(bench_file_path):
    benchmark_info = load_benchmark_info(bench_file_path)
    qc = QualityConverter()

    project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    input_file_path = os.path.join(project_root, benchmark_info["input_file"].strip("./"))
    binary_input_file_path = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'),
                                          benchmark_info["input_file_binary"].strip("./"))
    qc.fastq_loader(input_file_path)
    print(input_file_path)
    metrics_df = pd.DataFrame(
        columns=['Job Name', 'Quality Score PSNR', 'Quality Score MSE', 'Probability PSNR', 'Probability MSE'])

    for job in benchmark_info['jobs']:
        decompressed_output_path = get_decompressed_output_path(project_root, job, input_file_path,
                                                                binary_input_file_path)
        loader_method = determine_loader_method(job['name'])

        if decompressed_output_path and loader_method == "decompress_loader":
            qc.decompress_loader(decompressed_output_path, mode="FixedDiff")
            print(decompressed_output_path)
        elif decompressed_output_path and loader_method == "fastq_loader":
            qc.fastq_loader(decompressed_output_path, type="Decompressed")
            print(decompressed_output_path)

        if decompressed_output_path:
            psnr, mse, psnr_p, mse_p = qc.error_calculator()
            temp_df = pd.DataFrame([{
                'Job Name': job['name'] + job['options'][0],
                'Quality Score PSNR': psnr,
                'Quality Score MSE': mse,
                "Probability PSNR": psnr_p,
                "Probability MSE": mse_p
            }])
            metrics_df = pd.concat([metrics_df, temp_df], ignore_index=True)
    return metrics_df


if __name__ == "__main__":
    bench_file_path = '/home/tus53997/Benchmark_DNACompression/jobs/Cbench.json'

    metrics_df = metric_analysis(bench_file_path)
    metrics_df.to_csv('/home/tus53997/Benchmark_DNACompression/Analysis/metrics_df.csv')
    # metrics_df = pd.read_csv('/home/tus53997/Benchmark_DNACompression/Analysis/metrics_df.csv')

    compression_df = pd.read_csv('/home/tus53997/Benchmark_DNACompression/logs/compression_metrics.csv')

    parser_csv()
    Ratio_df = pd.read_csv('/home/tus53997/Benchmark_DNACompression/Analysis/ratio.csv')

    print("Compression: ", compression_df.shape)
    print("Ratio: ", Ratio_df.shape)
    print("Metric: ", metrics_df.shape)

    merged_df = pd.merge(compression_df, Ratio_df, left_on='job_id', right_on='job_id')
    # merged_df.to_csv("/home/tus53997/Benchmark_DNACompression/Analysis/merged_df_1.csv")

    merged_df2 = pd.merge(metrics_df, merged_df, left_on="Job Name", right_on="Compressor Name")
    merged_df.drop(columns=['Compressor Name'], inplace=True)
    merged_df2.to_csv('/home/tus53997/Benchmark_DNACompression/Analysis/merged_df.csv')
    print("Merging Done")


------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


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