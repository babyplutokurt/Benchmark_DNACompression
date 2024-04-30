import os
import json
import subprocess
from Scripts.Path_generator import PathGenerator
from Tool_paths import TOOL_PATHS
from Alignement_command_generator import ReferenceIndexerFromConfig
class AlignmentJobGenerator:
    def __init__(self, config_path):
        self.config_path = config_path
        self.indexer = ReferenceIndexerFromConfig(config_path)

    def submit_job(self, command, job_name, output_dir, dependency=None):
        """Function to submit a job to the queue system with optional dependency."""
        os.makedirs(output_dir, exist_ok=True)
        script_path = os.path.join(output_dir, f"{job_name}.sh")
        with open(script_path, 'w') as file:
            file.write(
                f"""#!/bin/sh
    #PBS -l walltime=168:00:00
    #PBS -N {job_name}
    #PBS -l nodes=1:ppn=24
    #PBS -o {output_dir}/{job_name}_output.log
    #PBS -e {output_dir}/{job_name}_error.log
    {'#PBS -W depend=afterok:' + dependency if dependency else ''}

    cd $PBS_O_WORKDIR
    source /home/tus53997/miniconda3/bin/activate compression

    {command}

    conda deactivate
    """)
        submission_command = f"qsub {script_path}"
        result = subprocess.run(submission_command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()

    def run(self):
        """Runs the job submission for indexing and alignment."""
        reference_indexed = self.indexer.config.get("reference_already", False)
        job_scripts_dir = "/home/tus53997/Benchmark_DNACompression/logs/Alignment_scripts"

        # Check if the reference needs indexing
        dependency_id = None
        if not reference_indexed:
            index_command = self.indexer.generate_index_command()
            dependency_id = self.submit_job(index_command, "Index_Reference", job_scripts_dir)
            print(f"Index job submitted with ID: {dependency_id}")

        # Submit alignment jobs
        for job_index in range(len(self.indexer.config.get('jobs', []))):
            alignment_command = self.indexer.generate_alignment_command(job_index)
            job_name = f"Alignment_Job_{job_index}"
            job_id = self.submit_job(alignment_command, job_name, job_scripts_dir, dependency=dependency_id)
            print(f"Alignment job {job_index} submitted with ID: {job_id}")


if __name__ == "__main__":
    config_path = "/home/tus53997/Benchmark_DNACompression/jobs/bench.json"
    job_generator = AlignmentJobGenerator(config_path)
    job_generator.run()
