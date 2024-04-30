def read_individual_quality_scores_from_sam(file_path):
    quality_scores = set()  # A set to store unique quality score characters

    try:
        with open(file_path, 'r') as file:
            for line in file:
                if not line.startswith('@'):  # Skip header lines
                    parts = line.strip().split()
                    if len(parts) > 10:  # Ensure the line has enough elements
                        quality_string = parts[10]  # Quality string is at index 10
                        quality_scores.update(quality_string)  # Add each character to the set
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return quality_scores

if __name__ == "__main__":
    file_path = '/home/tus53997/Benchmark_DNACompression/SAM/HG00097_CCAAGTCT-AAGGATGA_HCLHLDSXX_L004_001.R1.bin_-f_-1_5126799450_-M_REL_0.1_decompressed.sz.out.sam'
    unique_quality_char = read_individual_quality_scores_from_sam(file_path)
    print("Unique Quality Scores:")
    unique_quality_scores = set()
    for char in unique_quality_char:
        unique_quality_scores.add(ord(char))
    print(unique_quality_scores)
