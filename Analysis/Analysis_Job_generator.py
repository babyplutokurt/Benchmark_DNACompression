import subprocess
import os


def submit_analysis_job(analysis_script_path, conda_env_name="compression", job_name="analysis_job",
                        output_dir="/home/tus53997/Benchmark_DNACompression/logs"):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Define the job script content
    job_script_content = f"""#!/bin/bash
#PBS -N {job_name}
#PBS -l walltime=01:00:00
#PBS -l select=1:ncpus=1:mem=128gb
#PBS -j oe
#PBS -o {output_dir}/{job_name}_output.log

source /home/tus53997/miniconda3/bin/activate {conda_env_name}


cd /home/tus53997/Benchmark_DNACompression/Analysis
# Run the analysis Python script
python3 {analysis_script_path}

# Deactivate conda environment
conda deactivate
"""

    # Write the job script to a temporary file
    job_script_path = os.path.join(output_dir + '/Job_scripts', f"{job_name}_submit_script.sh")
    with open(job_script_path, "w") as script_file:
        script_file.write(job_script_content)

    # Submit the job using qsub
    try:
        submission_result = subprocess.run(["qsub", job_script_path], check=True, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE, text=True)
        print(f"Job '{job_name}' submitted successfully. Job ID: {submission_result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to submit job '{job_name}'. {e.stderr}")


# Example usage
if __name__ == "__main__":
    analysis_script_path = "/home/tus53997/Benchmark_DNACompression/Analysis/Metric_analysis.py"
    submit_analysis_job(analysis_script_path)