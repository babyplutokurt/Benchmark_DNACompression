import os


def analyze_fastq(file_path):
    # Initialize counters
    identifier_bytes = 0
    bases_bytes = 0
    quality_bytes = 0

    # Open and read the FASTQ file
    with open(file_path, 'r') as fastq_file:
        line_number = 0
        for line in fastq_file:
            # Remove newline characters to count bytes accurately
            stripped_line = line.rstrip('\n')
            line_bytes = len(stripped_line.encode('utf-8'))

            if line_number % 4 == 0:  # Identifier line
                identifier_bytes += line_bytes
            elif line_number % 4 == 1:  # Sequence (DNA bases) line
                bases_bytes += line_bytes
            elif line_number % 4 == 3:  # Quality line
                quality_bytes += line_bytes

            line_number += 1

    # Print results
    print(f"Total identifier bytes: {identifier_bytes}")
    print(f"Total DNA bases bytes: {bases_bytes}")
    print(f"Total quality score bytes: {quality_bytes}")
    return identifier_bytes, bases_bytes, quality_bytes


# Example usage
if __name__ == "__main__":
    file_path = '/home/tus53997/Benchmark_DNACompression/DecompressedOutput/HG00097_CCAAGTCT-AAGGATGA_HCLHLDSXX_L004_001.R2.bin_-f_-1_5126799450_-M_REL_0.9_decompressed.sz.out.fastq'  # Update with your FASTQ file path
    analyze_fastq(file_path)
