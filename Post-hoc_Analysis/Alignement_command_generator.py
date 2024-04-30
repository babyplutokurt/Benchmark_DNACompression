import os
import json
from Scripts.Path_generator import PathGenerator
from Tool_paths import TOOL_PATHS



class ReferenceIndexerFromConfig:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self.load_config()
        self.path_generator = PathGenerator(config_path)

    def load_config(self):
        with open(self.config_path) as json_file:
            return json.load(json_file)

    def generate_index_command(self):
        """Generate the BWA index command based on the reference file size."""
        reference_path = self.config.get("reference_file")
        if not reference_path:
            raise ValueError("Reference file path is missing in the configuration.")

        # Check if the path is absolute, if not, construct the full path
        if not os.path.isabs(reference_path):
            # Assuming the config file and the reference file are in the same directory
            reference_path = os.path.join(os.path.dirname(self.config_path), reference_path)

        file_size = os.path.getsize(reference_path)
        # 2GB in bytes
        two_gb_in_bytes = 2 * 1024 * 1024 * 1024

        # Use the bwa path from the TOOL_PATHS dictionary
        bwa_path = TOOL_PATHS.get("bwa")
        if not bwa_path:
            raise ValueError("BWA path is not defined in TOOL_PATHS.")

        if file_size > two_gb_in_bytes:
            return f"{bwa_path} index -a bwtsw {reference_path}"
        else:
            return f"{bwa_path} index {reference_path}"

    def generate_alignment_command(self, job_index):
        """Generate the BWA mem alignment command using decompressed FASTQ file paths."""

        file_paths_1 = self.path_generator.generate_file_paths_for_job(job_index, 0)
        file_paths_2 = self.path_generator.generate_file_paths_for_job(job_index, 1)

        read_group_info = "@RG\\tID:sample_1\\tLB:sample_1\\tPL:ILLUMINA\\tPM:HISEQ\\tSM:sample_1"
        reference_path = self.config.get("reference_file")
        if not os.path.isabs(reference_path):
            reference_path = os.path.join(os.path.dirname(self.config_path), reference_path)

        bwa_path = TOOL_PATHS.get("bwa")
        if not bwa_path:
            raise ValueError("BWA path is not defined in TOOL_PATHS.")

        decompressed_file_1 = file_paths_1["decompressed_file_path"]
        decompressed_file_2 = file_paths_2["decompressed_file_path"]

        # Construct the SAM directory path and filename
        sam_directory = os.path.join(self.path_generator.project_base_dir, 'SAM')
        os.makedirs(sam_directory, exist_ok=True)  # Ensure the SAM directory exists
        base_filename = os.path.basename(decompressed_file_1)
        sam_filename = base_filename.replace('.fastq', '.sam')
        alignment_name = os.path.join(sam_directory, sam_filename)

        alignment_command = f"{bwa_path} mem -t 24 -M -R '{read_group_info}' {reference_path} {decompressed_file_1} {decompressed_file_2} > {alignment_name}"
        return alignment_command


if __name__ == "__main__":
    config_path = "/home/tus53997/Benchmark_DNACompression/jobs/Cbench.json"
    indexer = ReferenceIndexerFromConfig(config_path)
    command = indexer.generate_alignment_command(1)
    print(command)
