import os
import json
from Tool_paths import TOOL_PATHS


class ReferenceIndexerFromConfig:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self.load_config()

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


if __name__ == "__main__":
    config_path = "/home/tus53997/Benchmark_DNACompression/jobs/Cbench.json"
    indexer = ReferenceIndexerFromConfig(config_path)
    command = indexer.generate_index_command()
    print(command)
