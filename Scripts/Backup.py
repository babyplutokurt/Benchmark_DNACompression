import json
from Compressor_paths import COMPRESSOR_PATHS
import os


class CommandGenerator:
    def __init__(self, config_name):
        self.project_base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
        self.jobs_dir = os.path.join(self.project_base_dir, 'jobs')
        self.config_path = os.path.join(self.jobs_dir, config_name)
        self.config = self.load_config()

    def load_config(self):
        with open(self.config_path) as json_file:
            return json.load(json_file)

    def generate_commands(self):
        raise NotImplementedError("Subclasses should implement this method.")


class SZ3CommandGenerator(CommandGenerator):
    def generate_command_for_job(self, job_index):
        # Ensure the job_index is within the range of available jobs for safety
        if job_index < 0 or job_index >= len(self.config['jobs']):
            raise ValueError("Job index out of range.")

        job = self.config['jobs'][job_index]
        if job['name'].upper() != "SZ3":
            return []  # Or raise an error if a non-SZ3 job is requested from this generator
        job_identifier = job['name'] + job['options'][0]
        executable_path = COMPRESSOR_PATHS.get("SZ3")
        if not executable_path:
            raise ValueError("Path for SZ3 compressor not found.")

        if len(job['options']) == 1:
            first_option_full = job['options'][0].replace(" ", "_")
            commands = []
            input_file_path = os.path.join(self.project_base_dir, self.config["input_file_binary"].strip("./"))
            output_file_name = f"{os.path.basename(input_file_path)}_{first_option_full}.sz"
            output_path = os.path.join(os.path.dirname(input_file_path), output_file_name)
            command = f"{executable_path} {' '.join(job['options'])} -i {input_file_path} -o {output_path}"
            commands.append(command)
            return commands, input_file_path, output_path, job_identifier, output_path
        elif len(job['options']) == 2:
            commands = []
            input_file_path = os.path.join(self.project_base_dir, self.config["input_file_binary"].strip("./"))
            first_option_full = job['options'][0].replace(" ", "_")
            output_file_name = f"{os.path.basename(input_file_path)}_{first_option_full}.sz"
            original_input_file_path = input_file_path

            for i, option in enumerate(job['options']):
                if i == 0:
                    output_path = os.path.join(self.project_base_dir, 'CompressedOutput', output_file_name)
                    command = f"{executable_path} {option} -i {input_file_path} -z {output_path}"
                    commands.append(command)
                    original_output_file_path = output_path
                elif i == 1:
                    input_file_path = output_path
                    output_file_name = os.path.basename(output_file_name).replace('.sz', '_decompressed.sz.out')
                    output_path = os.path.join(self.project_base_dir, 'DecompressedOutput', output_file_name)
                    command = f"{executable_path} {option} -z {input_file_path} -o {output_path}"
                    commands.append(command)
            return commands, original_input_file_path, original_output_file_path, job_identifier, output_path


class FQZCompCommandGenerator(CommandGenerator):
    def generate_command_for_job(self, job_index):
        # Ensure the job_index is within the range of available jobs for safety
        if job_index < 0 or job_index >= len(self.config['jobs']):
            raise ValueError("Job index out of range.")

        job = self.config['jobs'][job_index]
        if job['name'].upper() != "FQZCOMP":
            return []  # Or raise an error if a non-fqzcomp job is requested from this generator
        job_identifier = job['name'] + job['options'][0]
        executable_path = COMPRESSOR_PATHS.get("fqzcomp")
        if not executable_path:
            raise ValueError("Path for fqzcomp compressor not found.")

        commands = []
        input_file_path = os.path.join(self.project_base_dir, self.config["input_file"].strip("./"))
        first_option_full = job['options'][0].replace(" ", "_")
        output_file_name = f"{os.path.basename(input_file_path)}_{first_option_full}.fqz"
        original_input_file_path = input_file_path

        for option in job['options']:
            if "-d" in option:  # Assuming "-d" indicates a decompression job
                input_file_path = output_path
                output_file_name = os.path.basename(output_file_name).replace('.fqz', '_decompressed.fastq')
                output_path = os.path.join(self.project_base_dir, 'DecompressedOutput', output_file_name)
            else:  # Compression job
                output_file_name = f"{os.path.basename(input_file_path)}_{first_option_full}.fqz"
                output_path = os.path.join(self.project_base_dir, 'CompressedOutput', output_file_name)
                original_output_file_path = output_path

            command = f"{executable_path} {option} {input_file_path} {output_path}"
            commands.append(command)

        return commands, original_input_file_path, original_output_file_path, job_identifier, output_path


class SpringCommandGenerator(CommandGenerator):
    def __init__(self, config_name):
        super().__init__(config_name)
        self.executable_path = COMPRESSOR_PATHS.get('Spring')
        if not self.executable_path:
            raise ValueError("Path for Spring compressor not found.")

    def generate_command_for_job(self, job_index):
        if job_index < 0 or job_index >= len(self.config['jobs']):
            raise ValueError("Job index out of range.")

        job = self.config['jobs'][job_index]
        if job['name'].upper() != "SPRING":
            return []  # Optionally, raise an error instead
        job_identifier = job['name'] + job['options'][0]
        commands = []
        input_file_path = os.path.join(self.project_base_dir, self.config["input_file"].strip("./"))
        first_option_full = job['options'][0].replace(" ", "_")
        output_file_name = f"{os.path.basename(input_file_path)}_{first_option_full}.spring"
        original_input_file_path = input_file_path

        for option in job['options']:
            if "-d" in option:  # Assuming "-d" indicates a decompression job
                input_file_path = output_path
                output_file_name = os.path.basename(output_file_name).replace('.spring', '_decompressed.fastq')
                output_path = os.path.join(self.project_base_dir, 'DecompressedOutput', output_file_name)
            else:  # Compression job
                output_file_name = f"{os.path.basename(input_file_path)}_{first_option_full}.spring"
                output_path = os.path.join(self.project_base_dir, 'CompressedOutput', output_file_name)
                original_output_file_path = output_path

            command = f"{self.executable_path} {option} -i {input_file_path} -o {output_path}"
            commands.append(command)

        return (commands, original_input_file_path, original_output_file_path, job_identifier, output_path)


class CommandGeneratorWrapper:
    def __init__(self, config_name):
        self.config_name = config_name
        self.config = self._load_config(config_name)
        self.generators = {
            'SZ3': SZ3CommandGenerator(config_name),
            'FQZCOMP': FQZCompCommandGenerator(config_name),
            'SPRING': SpringCommandGenerator(config_name)
        }

    def _load_config(self, config_name):
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'jobs', config_name)
        with open(config_path) as json_file:
            return json.load(json_file)

    def generate_all_commands(self):
        all_commands = []
        for i, job in enumerate(self.config['jobs']):
            generator = self.generators.get(job['name'].upper())
            if generator:
                job_commands = generator.generate_command_for_job(i)
                all_commands.append(job_commands)  # Append commands for the specific job
            else:
                print(f"No generator found for {job['name']}. Skipping...")
        return all_commands


# Example usage
if __name__ == "__main__":
    wrapper = CommandGeneratorWrapper("/home/tus53997/Benchmark_DNACompression/jobs/Cbench.json")
    all_commands = wrapper.generate_all_commands()
    for command in all_commands:
        print(command)



import os
import subprocess
import psutil
import json
from Command_generator import CommandGeneratorWrapper
import csv


def generate_and_submit_job(job_name, commands, input_path, output_path, job_identifier, size_metrics, max_quality_char,
                            singularity_image="/home/tus53997/sz3_perf_amd.sif",
                            output_dir="/home/tus53997/Benchmark_DNACompression/logs/Job_scripts", dependency=""):
    os.makedirs(output_dir, exist_ok=True)
    log_path = "/home/tus53997/Benchmark_DNACompression/logs/logs"
    metrics_file_path = "/home/tus53997/Benchmark_DNACompression/logs/compression_metrics.csv"
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
    TOTAL_ORIGINAL_SIZE=$(echo "{sum(size_metrics[file]['original_size'] for file in size_metrics)}" | bc)
    TOTAL_COMPRESSED_SIZE=$(echo "{sum(size_metrics[file]['compressed_size'] for file in size_metrics if file != 'quality_identifiers.fastq')}" | bc)

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
                base_seq_path = "/home/tus53997/Benchmark_DNACompression/Fastq/Individual_fields/dna_bases.fastq"
                base_id_path = "/home/tus53997/Benchmark_DNACompression/Fastq/Individual_fields/base_identifiers.fastq"
                quality_id_path = ("/home/tus53997/Benchmark_DNACompression/Fastq/Individual_fields"
                                   "/quality_identifiers.fastq")
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
#PBS -l nodes=1:ppn=24
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


def generate_bash_script(fastq_file_path, output_directory):
    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)

    bash_script_content = f"""#!/bin/bash

# Extract the different fields from the FASTQ file
awk 'NR%4==1 {{print > "{output_directory}/base_identifiers.fastq"}} NR%4==2 {{print > "{output_directory}/dna_bases.fastq"}} NR%4==3 {{print > "{output_directory}/quality_identifiers.fastq"}}' {fastq_file_path}

# Compress each field with zstd
zstd --ultra --long -f {output_directory}/base_identifiers.fastq
zstd --ultra --long -f {output_directory}/dna_bases.fastq
zstd --ultra --long -f {output_directory}/quality_identifiers.fastq
"""
    return bash_script_content


def compress_fastq_fields(config_path):
    max_quality_char = '!'
    # Load the configuration file to get the FASTQ file path
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
        fastq_file_path = config["input_file"]

    with open('../' + fastq_file_path, 'r') as fastq_file:
        for i, line in enumerate(fastq_file):
            if (i + 1) % 4 == 0:  # Quality score lines
                max_quality_char = max(max_quality_char, max(line.strip(), default='!'))
                if i >= 1000:
                    break

    output_directory = "/home/tus53997/Benchmark_DNACompression/Fastq/Individual_fields"
    fastq_file_path = os.path.join("/home/tus53997/Benchmark_DNACompression/Scripts/../", fastq_file_path)
    bash_script = generate_bash_script(fastq_file_path, output_directory)

    script_path = "/home/tus53997/Benchmark_DNACompression/logs/Pre_warm_scripts/compress_fastq_fields.sh"
    with open(script_path, 'w') as script_file:
        script_file.write(bash_script)
    os.chmod(script_path, 0o755)
    subprocess.run(script_path, shell=True, check=True)
    size_metrics = {}
    files = ["base_identifiers.fastq", "dna_bases.fastq", "quality_identifiers.fastq"]

    # Calculate and store both original and compressed sizes for each file
    for file in files:
        original_path = os.path.join(output_directory, file)
        compressed_path = f"{original_path}.zst"
        original_size = os.path.getsize(original_path)
        compressed_size = os.path.getsize(compressed_path)

        # Store the sizes in the dictionary
        size_metrics[file] = {"original_size": original_size, "compressed_size": compressed_size}
    print(size_metrics)
    # Return the size metrics dictionary
    return size_metrics, max_quality_char


def main(config_name, size_metrics, max_quality_char):
    wrapper = CommandGeneratorWrapper(config_name)
    all_commands = wrapper.generate_all_commands()

    for i, job_commands_and_path in enumerate(all_commands):
        job_commands = job_commands_and_path[0]
        input_path = job_commands_and_path[1]
        output_path = job_commands_and_path[2]
        job_identifier = job_commands_and_path[3]
        print(job_identifier)
        print(job_commands)
        if job_commands:  # Ensure there are commands to execute
            job_name = f"job_{i}"  # Generate a unique job name, adjust as needed
            generate_and_submit_job(job_name, job_commands, input_path, output_path, job_identifier, size_metrics,
                                    max_quality_char)
            # print(job_name, job_commands, input_path, output_path, job_identifier)


if __name__ == "__main__":
    current_working_directory = os.getcwd()
    config_name = current_working_directory + "/../jobs/Cbench.json"
    size_metrics, max_quality_char = compress_fastq_fields(config_name)
    size_metrics_path = current_working_directory + '/../logs/size_metrics.json'
    with open(size_metrics_path, 'w') as file:
        json.dump(size_metrics, file, indent=4)
    print(f"Size metrics successfully saved to {size_metrics_path}.")
    filename = current_working_directory + '/../logs/compression_metrics.csv'
    header = ['job_id', 'Compressor Name', 'Time (seconds)', 'Ratio']
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
    print("max_quality_char: ", max_quality_char)
    print("max_quality_Value: ", ord(max_quality_char))
    main(config_name, size_metrics, max_quality_char)
