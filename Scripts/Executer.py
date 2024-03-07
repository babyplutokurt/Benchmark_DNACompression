import json
import subprocess
import os
import argparse
from CommandGenerator import generate_sz3_command, generate_fqzcomp_command, generate_fqzcomp_command_CompressDecompress

os_name = os.uname().sysname.lower()

# Submit jobs
print(f"Running on: {os_name}")


def execute_command(command):
    try:
        print(f"Executing command: {command}")
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate()

        output = output.decode('utf-8')
        error = error.decode('utf-8')

        if process.returncode == 0:
            print("Command executed successfully!")
            print("Output:\n", output)
            if error:
                print(error)
        else:
            print("Command failed with error:\n", error)
            return False  # Indicate failure to execute this command

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False  # Indicate an error occurred

    return True


def parse_argument():
    parser = argparse.ArgumentParser(description="Execute commands based on the specified configuration.")
    parser.add_argument('-c', '--config', type=str, help="Path to the configuration file",
                        default='/default/path/to/config.json')
    return parser.parse_args()


def parse_arguments():
    parser = argparse.ArgumentParser(description="Execute compression jobs based on the specified bench configuration.")
    parser.add_argument('-c', '--config', type=str, help="Path to the bench configuration file", required=True)
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
    execute_commands(commands)


def main():
    args = parse_arguments()
    bench_config_path = args.config

    try:
        with open(bench_config_path, 'r') as file:
            bench_config = json.load(file)
            job_files = bench_config.get("jobs", [])
            for job_file in job_files:
                print(f"Processing job configuration: {job_file}")
                execute_job_from_config(job_file)
    except FileNotFoundError:
        print(f"Could not find the bench configuration file: {bench_config_path}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the bench configuration file: {bench_config_path}")

if __name__ == "__main__":
    main()

"""
if __name__ == "__main__":
    args = parse_arguments()
    for config_name in args.config:  # Iterating over each specified config file
        print(f"Processing {config_name}")

        compressor_type = get_compressor_type(config_name)
        commands = []
        if compressor_type == 'sz3':
            commands.append(generate_sz3_command(config_name))  # Ensure this returns a list or wrap it in a list
        elif compressor_type == 'fqzcomp':
            commands = generate_fqzcomp_command_2(config_name)  # Assuming this returns a list of commands
        else:
            raise ValueError(f"Unsupported compressor specified: {compressor_type}")

        print(f"Executing commands for: {compressor_type}")
        execute_commands(commands)
"""