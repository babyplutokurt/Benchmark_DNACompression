import os
import subprocess
import psutil
import json
from Command_generator import CommandGeneratorWrapper


def generate_and_submit_job(job_name, commands, input_path, output_path, job_identifier, singularity_image="/home/tus53997/sz3_perf_amd.sif",
                            output_dir="/home/tus53997/Benchmark_DNACompression/logs/Job_scripts", dependency=""):
    os.makedirs(output_dir, exist_ok=True)
    log_path = "/home/tus53997/Benchmark_DNACompression/logs/logs"  # Directory to store logs
    metrics_file_path = "/home/tus53997/Benchmark_DNACompression/logs/compression_metrics.csv"
    os.makedirs(log_path, exist_ok=True)  # Ensure log directory exists

    # Check if metrics CSV file exists; if not, create it and add headers
    with open(metrics_file_path, 'w') as metrics_file:
        metrics_file.write("Compressor Name,Time (seconds),Ratio\n")

    for i, command in enumerate(commands):
        individual_job_name = f"{job_name}_{i}"
        job_script_path = os.path.join(output_dir, f"{individual_job_name}.sh")
        dependency = f"#PBS -W depend=afterok:{dependency}" if dependency else ""

        if i == 0:  # Adjust script for the first command to measure time and calculate compression ratio
            compression_perf_script = f"""
#!/bin/bash
START_TIME=$SECONDS
singularity exec --bind /home/tus53997:/mnt {singularity_image} {command}
END_TIME=$SECONDS
DURATION=$((END_TIME - START_TIME))

INPUT_SIZE=$(stat -c %s "{input_path}")
OUTPUT_SIZE=$(stat -c %s "{output_path}")
RATIO=$(echo "scale=2;  $INPUT_SIZE/$OUTPUT_SIZE" | bc)

echo "{job_identifier},$DURATION,$RATIO" >> "{metrics_file_path}"
"""
            command_script = compression_perf_script
        else:
            # For subsequent commands, simply execute without additional script adjustments
            command_script = f"singularity exec --bind /home/tus53997:/mnt {singularity_image} {command}"

        # Job template including the command script
        job_template = f"""#!/bin/sh
#PBS -l walltime=1:00:00
#PBS -N {individual_job_name}
#PBS -l nodes=1:ppn=1
#PBS -M taolue.yang@temple.edu
#PBS -o {log_path}/{individual_job_name}_output.log
#PBS -e {log_path}/{individual_job_name}_error.log
{dependency}

cd $PBS_O_WORKDIR
module load singularity
{command_script}
"""

        with open(job_script_path, 'w') as job_script:
            job_script.write(job_template)

        print(f"Job script generated: {job_script_path}")

        submission_command = f"qsub {job_script_path}"
        result = subprocess.run(submission_command, shell=True, check=True, capture_output=True, text=True)
        job_id = result.stdout.strip()
        print(f"Job '{individual_job_name}' submitted with ID {job_id}.")
        dependency = job_id  # Update for next iteration's dependency
    return dependency


def main():
    config_name = "/home/tus53997/Benchmark_DNACompression/jobs/Cbench.json"  # Specify your configuration file name here
    wrapper = CommandGeneratorWrapper(config_name)
    all_commands = wrapper.generate_all_commands()
    # print(all_commands)

    for i, job_commands_and_path in enumerate(all_commands):
        job_commands = job_commands_and_path[0]
        input_path = job_commands_and_path[1]
        output_path = job_commands_and_path[2]
        job_identifier = job_commands_and_path[3]
        if job_commands:  # Ensure there are commands to execute
            job_name = f"job_{i}"  # Generate a unique job name, adjust as needed
            generate_and_submit_job(job_name, job_commands, input_path, output_path, job_identifier)
            # print(job_name, job_commands, input_path, output_path, job_identifier)


if __name__ == "__main__":
    main()
