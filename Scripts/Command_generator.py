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
    def generate_command_for_job(self, job_index, input_file_index):
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
            input_file_path = os.path.join(self.project_base_dir, self.config["input_file_binary"][input_file_index].strip("./"))
            output_file_name = f"{os.path.basename(input_file_path)}_{first_option_full}.sz"
            output_path = os.path.join(os.path.dirname(input_file_path), output_file_name)
            command = f"{executable_path} {' '.join(job['options'])} -i {input_file_path} -o {output_path}"
            commands.append(command)
            return commands, input_file_path, output_path, job_identifier, output_path
        elif len(job['options']) == 2:
            commands = []
            input_file_path = os.path.join(self.project_base_dir, self.config["input_file_binary"][input_file_index].strip("./"))
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
    def generate_command_for_job(self, job_index, input_file_index):
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
        input_file_path = os.path.join(self.project_base_dir, self.config["input_file"][input_file_index].strip("./"))
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

    def generate_command_for_job(self, job_index, input_file_index):
        if job_index < 0 or job_index >= len(self.config['jobs']):
            raise ValueError("Job index out of range.")

        job = self.config['jobs'][job_index]
        if job['name'].upper() != "SPRING":
            return []  # Optionally, raise an error instead
        job_identifier = job['name'] + job['options'][0]
        commands = []
        input_file_path = os.path.join(self.project_base_dir, self.config["input_file"][input_file_index].strip("./"))
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
        all_commands_for_files = []
        for j in range(len(self.config['input_file'])):  # For each input file
            commands_for_current_file = []  # Store all commands related to this file
            for i, job in enumerate(self.config['jobs']):  # For each job
                generator = self.generators.get(job['name'].upper())
                if generator:
                    job_commands = generator.generate_command_for_job(i, j)
                    commands_for_current_file.append(job_commands)  # Add to the list for the current file
                else:
                    print(f"No generator found for {job['name']}. Skipping...")
            all_commands_for_files.append(commands_for_current_file)
        return all_commands_for_files


# Example usage
if __name__ == "__main__":
    wrapper = CommandGeneratorWrapper("/home/tus53997/Benchmark_DNACompression/jobs/bench.json")
    all_commands = wrapper.generate_all_commands()
    for command in all_commands:
        print(len(command))
        print(command)
        print(command[2][0])
        print(command[2][1])
        print(command[2][2])
        print(command[2][3])
