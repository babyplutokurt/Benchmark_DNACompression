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

    def get_input_file_path(self, job_name):
        # Choose input file based on compressor type
        if job_name.upper() in ["SZ3"]:
            return self.get_full_path(self.config.get("input_file_binary", ""))
        else:
            return self.get_full_path(self.config.get("input_file", ""))

    def generate_file_paths_for_job(self, job_index):
        if job_index < 0 or job_index >= len(self.config['jobs']):
            raise ValueError("Job index out of range.")

        job = self.config['jobs'][job_index]
        job_name = job['name']
        input_file_path = self.get_input_file_path(job_name)

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
        sanitized_option_str = option_str.replace(" ", "_")
        base_output_file_name = f"{os.path.basename(input_file_path)}_{sanitized_option_str}"

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
    for i in range(len(path_gen.config['jobs'])):
        file_paths = path_gen.generate_file_paths_for_job(i)
        print(f"Job {i}:")
        print("Compressed File Path:", file_paths["compressed_file_path"])
        print(Size_checker.get_file_size(file_paths["compressed_file_path"]))
        print("Decompressed File Path:", file_paths["decompressed_file_path"])
        print(Size_checker.get_file_size(file_paths["decompressed_file_path"]))
        print("-" * 40)
