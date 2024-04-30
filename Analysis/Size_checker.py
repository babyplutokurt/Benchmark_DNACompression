import os

def get_file_size(file_path):
    try:
        size = os.path.getsize(file_path)
        return size
    except OSError as e:
        print(f"Error: {e}")
        return None

# Example usage
if __name__ == "__main__":
    file_path = "/home/tus53997/Benchmark_DNACompression/DecompressedOutput/HG00097_CCAAGTCT-AAGGATGA_HCLHLDSXX_L004_001.R1.bin_-f_-1_5126799450_-M_REL_0.1_decompressed.sz.out.fastq"  # Replace with the actual file path
    size = get_file_size(file_path)
    if size is not None:
        print(f"The size of the file '{file_path}' is {size} bytes.")
    else:
        print("Could not retrieve the file size.")