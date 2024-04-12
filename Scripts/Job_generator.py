import os
import subprocess
import psutil
import json
from Command_generator import CommandGeneratorWrapper
import csv


def generate_and_submit_job(job_name, commands, input_path, output_path, job_identifier, size_metric, max_quality_char,
                            file_index,
                            singularity_image="/home/tus53997/sz3_perf_amd.sif",
                            output_dir="/home/tus53997/Benchmark_DNACompression/logs/Job_scripts", dependency=""):
    os.makedirs(output_dir, exist_ok=True)
    log_path = "/home/tus53997/Benchmark_DNACompression/logs/logs"
    metrics_file_path = f"/home/tus53997/Benchmark_DNACompression/logs/compression_metrics{file_index}.csv"
    os.makedirs(log_path, exist_ok=True)

    for i, command in enumerate(commands):
        individual_job_name = f"{job_name}_{i}"
        job_script_path = os.path.join(output_dir, f"{individual_job_name}.sh")
        dependency = f"#PBS -W depend=afterok:{dependency}" if dependency else ""
        reconstruct_script = ""

        if i == 0:  # Adjust script for the first command to measure time and calculate compression ratio
            # Determine compressor type for logging
            compressor_type = "SZ3" if 'SZ3' in command else "Other"

            # Script to calculate duration and compression ratio
            compression_perf_script = f"""
#!/bin/bash
START_TIME=$SECONDS
singularity exec --bind /home/tus53997:/mnt {singularity_image} {command}
END_TIME=$SECONDS
DURATION=$((END_TIME - START_TIME))

# Differentiate the handling based on the compressor type
if [ "{compressor_type}" == "SZ3" ]; then
    INPUT_SIZE=$(stat -c %s "{input_path}")
    OUTPUT_SIZE=$(stat -c %s "{output_path}")
    ADJUSTED_INPUT_SIZE=$((INPUT_SIZE / 4))
    TOTAL_ORIGINAL_SIZE=$(echo "{sum(size_metric[file]['original_size'] for file in size_metric)}" | bc)
    TOTAL_COMPRESSED_SIZE=$(echo "{sum(size_metric[file]['compressed_size'] for file in size_metric if file != 'quality_identifiers.fastq')}" | bc)

    FINAL_ORIGINAL_SIZE=$(($ADJUSTED_INPUT_SIZE + $TOTAL_ORIGINAL_SIZE))
    FINAL_COMPRESSED_SIZE=$(($OUTPUT_SIZE + $TOTAL_COMPRESSED_SIZE))

    RATIO=$(echo "scale=2; $FINAL_ORIGINAL_SIZE / $FINAL_COMPRESSED_SIZE" | bc)
else
    INPUT_SIZE=$(stat -c %s "{input_path}")
    OUTPUT_SIZE=$(stat -c %s "{output_path}")
    RATIO=$(echo "scale=2; $INPUT_SIZE / $OUTPUT_SIZE" | bc)
fi

echo "{individual_job_name},{job_identifier},$DURATION,$RATIO" >> "{metrics_file_path}"
"""

            command_script = compression_perf_script
        else:
            # For subsequent commands, simply execute without additional script adjustments
            command_script = f"singularity exec --bind /home/tus53997:/mnt {singularity_image} {command}"
            compressor_type = "SZ3" if 'SZ3' in command else "Other"
            if compressor_type == "SZ3":
                base_seq_path = f"/home/tus53997/Benchmark_DNACompression/Fastq/Individual_fields/dna_bases{file_index}.fastq"
                base_id_path = f"/home/tus53997/Benchmark_DNACompression/Fastq/Individual_fields/base_identifiers{file_index}.fastq"
                quality_id_path = f"/home/tus53997/Benchmark_DNACompression/Fastq/Individual_fields/quality_identifiers{file_index}.fastq"
                sz_output_path = ""

                normalized_path = os.path.normpath(output_path)
                directory_path = os.path.dirname(normalized_path)
                filename = os.path.basename(normalized_path)
                sz_output_path = directory_path + '/../DecompressedOutput/' + filename[:-3] + '_decompressed.sz.out'

                reconstructed_fastq_path = sz_output_path[:-4] + ".fastq" if output_path.endswith(
                    '.out') else sz_output_path + ".fastq"
                reconstruct_script = f"""
python -c "import sys; sys.path.append('/home/tus53997/Benchmark_DNACompression/Scripts'); from SZ3_Decompress_Assembler import reconstruct_fastq; reconstruct_fastq('{base_seq_path}',
        '{base_id_path}',
        '{quality_id_path}',
        '{sz_output_path}',
        '{reconstructed_fastq_path}',
        max_quality_char='{max_quality_char}')"
"""

        # Job template including the command script
        job_template = f"""#!/bin/sh
#PBS -l walltime=1:00:00
#PBS -N {individual_job_name}
#PBS -l nodes=1:ppn=12
#PBS -M taolue.yang@temple.edu
#PBS -o {log_path}/{individual_job_name}_output.log
#PBS -e {log_path}/{individual_job_name}_error.log
{dependency}



cd $PBS_O_WORKDIR
module load singularity
{command_script}

source /home/tus53997/miniconda3/bin/activate compression
{reconstruct_script}
conda deactivate
"""

        with open(job_script_path, 'w') as job_script:
            job_script.write(job_template)

        print(f"Job script generated: {job_script_path}")

        submission_command = f"qsub {job_script_path}"
        result = subprocess.run(submission_command, shell=True, check=True, capture_output=True, text=True)
        job_id = result.stdout.strip()
        print(f"Job '{individual_job_name}' submitted with ID {job_id}.")
        dependency = job_id

    return dependency


def generate_bash_script(fastq_file_path, output_directory, index):
    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)

    bash_script_content = f"""#!/bin/bash

# Extract the different fields from the FASTQ file
awk 'NR%4==1 {{print > "{output_directory}/base_identifiers{index}.fastq"}} NR%4==2 {{print > "{output_directory}/dna_bases{index}.fastq"}} NR%4==3 {{print > "{output_directory}/quality_identifiers{index}.fastq"}}' {fastq_file_path}

# Compress each field with zstd
zstd --ultra --long -f {output_directory}/base_identifiers{index}.fastq
zstd --ultra --long -f {output_directory}/dna_bases{index}.fastq
zstd --ultra --long -f {output_directory}/quality_identifiers{index}.fastq
"""
    return bash_script_content


def compress_fastq_fields(config_path):
    max_quality_char = '!'
    # Load the configuration file to get the FASTQ file paths
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
        fastq_files = config["input_file"]

    # Ensure fastq_files is a list for uniform handling
    if not isinstance(fastq_files, list):
        fastq_files = [fastq_files]

    size_metrics = {}
    output_directory = "/home/tus53997/Benchmark_DNACompression/Fastq/Individual_fields"

    for index, fastq_file in enumerate(fastq_files):
        fastq_file_path = os.path.join("/home/tus53997/Benchmark_DNACompression/Scripts/../", fastq_file)
        bash_script = generate_bash_script(fastq_file_path, output_directory, index)

        script_path = f"/home/tus53997/Benchmark_DNACompression/logs/Pre_warm_scripts/compress_fastq_fields_{os.path.basename(fastq_file)}.sh"
        with open(script_path, 'w') as script_file:
            script_file.write(bash_script)
        os.chmod(script_path, 0o755)
        subprocess.run(script_path, shell=True, check=True)

        file_size_metrics = {}
        # Using f-string to incorporate index into filenames
        files = [f"base_identifiers{index}.fastq", f"dna_bases{index}.fastq", f"quality_identifiers{index}.fastq"]
        for file in files:
            original_path = os.path.join(output_directory, file)
            compressed_path = f"{original_path}.zst"
            original_size = os.path.getsize(original_path)
            compressed_size = os.path.getsize(compressed_path)
            # Store the sizes in the dictionary under the file name including the index
            file_size_metrics[file] = {"original_size": original_size, "compressed_size": compressed_size}

        # Update size_metrics with the metrics for the current file, including the index in the key
        size_metrics[f"file_{index}"] = file_size_metrics

        # Calculate max_quality_char across all files
        with open(fastq_file_path, 'r') as fastq_file:
            for i, line in enumerate(fastq_file):
                if (i + 1) % 4 == 0:  # Quality score lines
                    max_quality_char = max(max_quality_char, max(line.strip(), default='!'))
                    if i >= 1000:
                        break

    print(size_metrics)
    return size_metrics, max_quality_char


def main(config_name, size_metrics, max_quality_char):
    wrapper = CommandGeneratorWrapper(config_name)
    all_commands_global = wrapper.generate_all_commands()

    for file_index, all_commands in enumerate(all_commands_global):
        for i, job_commands_and_path in enumerate(all_commands):
            print(job_commands_and_path)
            job_commands = job_commands_and_path[0]
            input_path = job_commands_and_path[1]
            output_path = job_commands_and_path[2]
            job_identifier = job_commands_and_path[3]
            print(job_identifier)
            print(job_commands)
            if job_commands:  # Ensure there are commands to execute
                job_name = f"job_input{file_index}_{i}"
                metric_name = f'file_{file_index}'  # Generate a unique job name, adjust as needed
                size_metric = size_metrics[metric_name]
                generate_and_submit_job(job_name, job_commands, input_path, output_path, job_identifier, size_metric,
                                        max_quality_char, file_index)
                # print(job_name, job_commands, input_path, output_path, job_identifier)


if __name__ == "__main__":
    current_working_directory = os.getcwd()
    config_name = current_working_directory + "/../jobs/Cbench.json"
    size_metrics, max_quality_char = compress_fastq_fields(config_name)

    size_metrics_path = current_working_directory + '/../logs/size_metrics.json'
    with open(size_metrics_path, 'w') as file:
        json.dump(size_metrics, file, indent=4)
    print(f"Size metrics successfully saved to {size_metrics_path}.")

    # Determine the number of input files based on the length of the 'size_metrics' dictionary
    num_input_files = len(size_metrics)

    # Create a CSV file for each input file
    for i in range(num_input_files):
        filename = current_working_directory + f'/../logs/compression_metrics{i}.csv'
        header = ['job_id', 'Compressor Name', 'Time (seconds)', 'Ratio']
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)  # Ensure header is written inside the 'with open' block

    print("max_quality_char: ", max_quality_char)
    print("max_quality_Value: ", ord(max_quality_char))
    main(config_name, size_metrics, max_quality_char)
