import json
import os
import argparse
import subprocess
from CommandGenerator import generate_sz3_command, generate_fqzcomp_command, generate_fqzcomp_command_CompressDecompress

os_name = os.uname().sysname.lower()

# Submit jobs
print(f"Running on: {os_name}")


def execute_command(command):
    log_file_path = "/home/tus53997/Benchmark_DNACompression/logs/logfile.txt"  # Update this path to your log file location

    try:
        print(f"Executing command: {command}")
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate()

        output = output.decode('utf-8')
        error = error.decode('utf-8')

        with open(log_file_path, 'a') as log_file:  # Open the log file in append mode
            log_file.write(f"Command: {command}\n")  # Log the command
            log_file.write("Output:\n" + output + "\n")  # Log the output
            if error:
                log_file.write("Error:\n" + error + "\n")  # Log the error if any

        if process.returncode == 0:
            print("Command executed successfully!")
            print("Output:\n", output)
            if error:
                print("Error:\n", error)
        else:
            print("Command failed with error:\n", error)
            return False  # Indicate failure to execute this command

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        with open(log_file_path, 'a') as log_file:  # Ensure that even script errors are logged
            log_file.write(f"An error occurred: {str(e)}\n")
        return False  # Indicate an error occurred

    return True


def parse_argument():
    parser = argparse.ArgumentParser(description="Execute commands based on the specified configuration.")
    parser.add_argument('-c', '--config', type=str, help="Path to the configuration file",
                        default='/default/path/to/config.json')
    return parser.parse_args()


def get_compressor_type(config_name):
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'jobs', config_name)
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config.get("compressor")


def execute_commands(commands):
    for command in commands:
        if not execute_command(command):  # If a command fails or an error occurs, stop the execution
            print("Stopping execution due to failure.")
            break


def execute_job_from_config(config_name):
    compressor_type = get_compressor_type(config_name)
    commands = []
    if compressor_type == 'sz3':
        commands.append(generate_sz3_command(config_name))
    elif compressor_type == 'fqzcomp':
        commands = generate_fqzcomp_command_CompressDecompress(config_name)
    else:
        print(f"Unsupported compressor specified: {compressor_type}")
        return  # Skip this job

    print(f"Executing commands for: {compressor_type}")
    print("All commands for this job: ", commands)
    execute_commands(commands)


def create_commands_from_config(config_name):
    compressor_type = get_compressor_type(config_name)
    commands = []
    if compressor_type == 'sz3':
        commands = generate_sz3_command(config_name)
    elif compressor_type == 'fqzcomp':
        commands = generate_fqzcomp_command_CompressDecompress(config_name)
    else:
        print(f"Unsupported compressor specified: {compressor_type}")
        return  # Skip this job

    print(f"Executing commands for: {compressor_type}")
    print("All commands for this job: ", commands)
    return commands


def parse_arguments():
    parser = argparse.ArgumentParser(description="Execute compression jobs based on the specified bench configuration.")
    parser.add_argument('-c', '--config', type=str, help="Path to the bench configuration file", required=True)
    return parser.parse_args()


def generate_and_submit_job(job_name, commands, singularity_image="sz3_perf_amd.sif",
                            output_dir="/home/tus53997/Benchmark_DNACompression/jobs"):
    # Define the path for the generated job script
    job_script_path = os.path.join(output_dir, f"{job_name}.sh")

    # Job script template incorporating Singularity
    job_template = f"""#!/bin/sh
#PBS -l walltime=1:00:00
#PBS -N {job_name}
#PBS -l nodes=1:ppn=1
#PBS -M taolue.yang@temple.edu
#PBS -m abe
#PBS -o {output_dir}/{job_name}_output.log
#PBS -e {output_dir}/{job_name}_error.log

# Change to directory where 'qsub' was called
cd $PBS_O_WORKDIR

# Load the singularity module
module load singularity
"""

    # Append commands to execute within the Singularity container
    for command in commands:
        singularity_command = f"singularity exec --bind /home/tus53997:/mnt {singularity_image} {command} \n"
        job_template += singularity_command

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Write the job script
    with open(job_script_path, 'w') as job_script:
        job_script.write(job_template)

    print(f"Job script generated: {job_script_path}")

    # Submit the job
    submission_command = f"qsub {job_script_path}"
    subprocess.run(submission_command, shell=True, check=True)
    print(f"Job '{job_name}' submitted.")


def main():
    print("Running on Main")
    args = parse_arguments()
    bench_config_path = args.config
    print("Args Config: ", bench_config_path)

    try:
        with open(bench_config_path, 'r') as file:
            bench_config = json.load(file)
            job_files = bench_config.get("jobs", [])
            for job_file in job_files:
                print(f"Processing job configuration: {job_file}")
                job_commands = create_commands_from_config(job_file)
                if job_commands:  # Ensure commands were generated
                    job_name = os.path.splitext(job_file)[0] + "_job"  # e.g., "sz3" for "sz3.json"
                    generate_and_submit_job(job_name, job_commands)
    except FileNotFoundError:
        print(f"Could not find the bench configuration file: {bench_config_path}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the bench configuration file: {bench_config_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error submitting job: {str(e)}")


if __name__ == "__main__":
    main()
