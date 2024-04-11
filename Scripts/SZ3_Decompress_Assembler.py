import numpy as np
import math
from Bio import SeqIO


def reconstruct_fastq(base_seq_path, base_id_path, quality_id_path, binary_float_path, output_fastq_path,
                      max_quality_char='J'):
    """
    Reconstruct a FASTQ file from its components and a binary sequence of quality scores.
    """
    # Load the binary quality scores as a numpy array
    quality_floats = np.fromfile(binary_float_path, dtype=np.float32)

    max_quality_score = ord(max_quality_char) - ord('!')

    # Function to convert float quality scores back to characters
    def float_to_quality(quality_float):
        decompressed_score = round(quality_float * max_quality_score)
        decompressed_score = min(decompressed_score, max_quality_score)
        return chr(decompressed_score + ord('!'))

    with open(base_seq_path) as base_seqs, open(base_id_path) as base_ids, \
            open(quality_id_path) as quality_ids, open(output_fastq_path, 'w') as output_file:
        float_index = 0  # Index to track position in the binary sequence
        for base_id, base_seq, quality_id in zip(base_ids, base_seqs, quality_ids):
            base_seq = base_seq.strip()
            quality_seq_length = len(base_seq)

            # Read the corresponding length of quality scores from the binary sequence
            quality_floats_segment = quality_floats[float_index:float_index + quality_seq_length]
            quality_scores = ''.join([float_to_quality(q) for q in quality_floats_segment])

            # Increment float_index for the next sequence
            float_index += quality_seq_length

            # Write the assembled FASTQ entry
            output_file.write(f"{base_id}{base_seq}\n{quality_id}{quality_scores}\n")


if __name__ == "__main__":
    reconstruct_fastq('/home/tus53997/Benchmark_DNACompression/Fastq/Individual_fields/dna_bases.fastq',
                      '/home/tus53997/Benchmark_DNACompression/Fastq/Individual_fields/base_identifiers.fastq',
                      '/home/tus53997/Benchmark_DNACompression/Fastq/Individual_fields/quality_identifiers.fastq',
                      '/home/tus53997/Benchmark_DNACompression/DecompressedOutput/ERR103405_2_F.bin_-f_-1_63866600_-M_REL_0_decompressed.sz.out',
                      '/home/tus53997/Benchmark_DNACompression/DecompressedOutput/ERR103405_2_F.bin_-f_-1_63866600_-M_REL_0_decompressed.sz.fastq')
