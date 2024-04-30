import os
import json
from Analysis import Size_checker


class PathGenerator:
    def __init__(self, config_path):
        self.config_path = config_path
        self.project_base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
        self.config = self.load_config()

    def load_config(self):
        with open(self.config_path) as json_file:
            return json.load(json_file)

    def get_full_path(self, relative_path):
        if os.path.isabs(relative_path):
            return relative_path
        return os.path.join(self.project_base_dir, relative_path.strip("./\\"))

    def get_input_file_path(self, job_name, file_index):
        # Adjust method to handle list of input files based on file_index
        input_files = self.config.get("input_file_binary", []) if job_name.upper() in ["SZ3"] else self.config.get(
            "input_file", [])
        # Ensure input_files is always a list for uniform processing
        if not isinstance(input_files, list):
            input_files = [input_files]
        # Return the full path of the input file selected by file_index
        if 0 <= file_index < len(input_files):
            return self.get_full_path(input_files[file_index])
        else:
            raise IndexError(f"File index {file_index} is out of range for the input files.")

    def generate_file_paths_for_job(self, job_index, file_index):
        if job_index < 0 or job_index >= len(self.config['jobs']):
            raise ValueError("Job index out of range.")

        job = self.config['jobs'][job_index]
        job_name = job['name']
        input_file_path = self.get_input_file_path(job_name, file_index)

        # Determine the file suffix based on compressor type
        suffix_mapper = {
            "SZ3": ".sz",
            "FQZCOMP": ".fqz",
            "SPRING": ".spring"
        }
        decompress_suffix_mapper = {
            "SZ3": "_decompressed.sz.out",
            "FQZCOMP": "_decompressed",
            "SPRING": "_decompressed"
        }
        suffix = suffix_mapper.get(job_name.upper(), ".out")
        decompress_suffix = decompress_suffix_mapper.get(job_name.upper(), "_decompressed.out")

        option_str = job['options'][0]  # Assuming the first option is used for naming
        sanitized_option_str = option_str.replace(" ", "_").replace("/", "_")

        # Incorporate file_index into the file name to ensure uniqueness across multiple input files
        base_filename = os.path.basename(input_file_path)
        base_output_file_name = f"{base_filename}_{sanitized_option_str}"

        compressed_output_dir = os.path.join(self.project_base_dir, 'CompressedOutput')
        decompressed_output_dir = os.path.join(self.project_base_dir, 'DecompressedOutput')

        compressed_file_name = f"{base_output_file_name}{suffix}"
        decompressed_file_name = f"{base_output_file_name}{decompress_suffix}.fastq"

        compressed_file_path = os.path.join(compressed_output_dir, compressed_file_name)
        decompressed_file_path = os.path.join(decompressed_output_dir, decompressed_file_name)

        return {
            "compressed_file_path": compressed_file_path,
            "decompressed_file_path": decompressed_file_path
        }


# Example usage:
if __name__ == "__main__":
    config_name = "/home/tus53997/Benchmark_DNACompression/jobs/Cbench.json"  # Adjust the path as necessary
    path_gen = PathGenerator(config_name)
    file_indices = range(len(path_gen.config.get("input_file", [])))  # Or input_file_binary for SZ3
    for file_index in file_indices:
        for i in range(len(path_gen.config['jobs'])):
            file_paths = path_gen.generate_file_paths_for_job(i, file_index)
            print(f"File {file_index}, Job {i}:")
            print("Compressed File Path:", file_paths["compressed_file_path"])
            print(Size_checker.get_file_size(file_paths["compressed_file_path"]))
            print("Decompressed File Path:", file_paths["decompressed_file_path"])
            print(Size_checker.get_file_size(file_paths["decompressed_file_path"]))
            print("-" * 40)
