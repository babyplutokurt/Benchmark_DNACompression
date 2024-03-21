import os

def get_file_size(file_path):
    try:
        size = os.path.getsize(file_path)
        return size
    except OSError as e:
        print(f"Error: {e}")
        return None

# Example usage
file_path = "/home/tus53997/Benchmark_DNACompression/binFile/ERR103405_2_F.bin_-a_-f_-M_ABS_0.1_-2_152_420175.sz"  # Replace with the actual file path
size = get_file_size(file_path)
if size is not None:
    print(f"The size of the file '{file_path}' is {size} bytes.")
else:
    print("Could not retrieve the file size.")