import subprocess
import os
import pandas as pd
import json
from QualityConverter import QualityConverter  # Assuming the class you've shared is saved as QualityConverter.py


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
    compression_df = pd.read_csv('/home/tus53997/Benchmark_DNACompression/logs/compression_metrics.csv')
    merged_df = pd.merge(metrics_df, compression_df, left_on="Job Name", right_on="Compressor Name")
    merged_df.drop(columns=['Compressor Name'], inplace=True)
    print(metrics_df)

    merged_df.to_csv('/home/tus53997/Benchmark_DNACompression/Analysis/merged_df.csv')

    print(merged_df.shape)
