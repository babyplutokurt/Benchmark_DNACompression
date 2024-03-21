import numpy as np
from Bio import SeqIO
import math


class QualityConverter:
    def __init__(self, error_bound=0.2):
        """
        Initialize the QualityConverter object.

        Parameters:
        error_bound (float): Error bound for determining the conversion mode.
        """
        self.error_bound = error_bound
        self.rawQuality = None
        self.decompressQuality = None
        self.maxQualityScore = None
        self.minQualityScore = None

    def QtoP(self, quality):
        return 10 ** (-quality / 10)

    def PtoQ(self, probability):
        return -10 * math.log10(probability)

    def convert_to_integer(self, matrix):
        """
        Convert float numbers in a 2-dimensional numpy matrix to integers based on the mode determined by the range of numbers.

        Parameters:
        matrix (numpy.ndarray): 2-dimensional numpy matrix

        Returns:
        numpy.ndarray: Matrix with float numbers converted to integers.
        """
        # Check if the input is a numpy array
        if not isinstance(matrix, np.ndarray):
            raise ValueError("Input matrix must be a numpy array")

        # Check if the input matrix is 2-dimensional
        if len(matrix.shape) != 2:
            raise ValueError("Input matrix must be 2-dimensional")

        # Calculate the range of values in the matrix
        value_range = np.max(matrix) - np.min(matrix)

        # Check if the range of values is smaller than 1 + ErrorBound
        if value_range < (1 + self.error_bound):
            # Convert based on -10 * log10(Value)
            converted_matrix = -10 * np.log10(matrix)
            # Round after conversion
            converted_matrix = np.round(converted_matrix).astype(int)
        else:
            # If the range is larger, simply round the values
            converted_matrix = np.round(matrix).astype(int)
        self.decompressQuality = converted_matrix
        return converted_matrix

    def decompress_loader(self, file_path, mode="Probability"):
        """
        Load a binary file of float values to self.decompressQuality.

        Parameters:
        file_path (str): Path to the binary file.

        Returns:
        None
        """
        negative_count = 0

        # Load binary file into a NumPy array
        def quality_score(e):
            nonlocal negative_count
            if e <= 0:
                # Return a default value (or handle the error as needed)
                e = abs(e) + 0.0000000000001
                negative_count += 1
                # return 42
            res = -10 * math.log10(e)
            if res > 42:
                res = 42
            return res

        def fixedDiff(q):
            res = math.ceil(q * self.maxQualityScore)
            if res <= 2:
                res = 2
            elif res >= 42:
                res = 42
            return res

        decompress_data = np.fromfile(file_path, dtype=np.float32)

        # Reshape the NumPy array to match the shape of self.rawQuality
        num_rows = self.rawQuality.shape[0] if self.rawQuality is not None else 152
        num_cols = -1  # We'll find the actual number of columns later
        if decompress_data.size % num_rows == 0:
            num_cols = decompress_data.size // num_rows
        else:
            raise ValueError("The size of the decompressed data is not compatible with the shape of self.rawQuality")

        self.decompressQuality = decompress_data.reshape((num_rows, num_cols))
        if mode == "Probability":  # From Probability to restore Quality Score
            self.decompressQuality = np.vectorize(quality_score)(self.decompressQuality)
        elif mode == "FixedDiff":
            self.decompressQuality = np.vectorize(fixedDiff)(self.decompressQuality)
        print("Exceed 42 count: ", negative_count)
        return

    def fastq_loader(self, file_path, mode="Probability", type="Raw"):
        """
        Load a FASTQ file, extract quality scores, and convert them to integers using Biopython.

        Parameters:
        file_path (str): Path to the FASTQ file.

        Returns:
        numpy.ndarray: Matrix of quality scores converted to integers.
        """

        def probability_helper(q):
            return 10 ** (-q / 10)

        quality_scores = []
        for record in SeqIO.parse(file_path, "fastq"):
            # Check if the quality scores are integers (sometimes they are)
            if isinstance(record.letter_annotations["phred_quality"][0], int):
                scores = record.letter_annotations["phred_quality"]
            else:
                scores = [ord(char) - 33 for char in record.letter_annotations["phred_quality"]]
            quality_scores.append(scores)

        # Convert the list of lists to a numpy array
        quality_matrix = np.array(quality_scores)

        # Convert quality scores to integers based on the error_bound
        # converted_quality_matrix = self.convert_to_integer(quality_matrix)
        if type == "Raw":
            self.rawQuality = quality_matrix
            self.minQualityScore = np.min(quality_matrix)
            self.maxQualityScore = np.max(quality_matrix)
        elif type == "Decompressed":
            self.decompressQuality = quality_matrix
        return

    def fastq_writer(self, file_path, output_path, mode="Probability", buffer_size=500):
        """
        Retrieve quality scores from a FASTQ file, convert them to float, and write them to a binary file.

        Parameters:
        file_path (str): Path to the input FASTQ file.
        output_path (str): Path to the output binary file.

        Returns:
        None
        """

        def probability_helper(q):
            return 10 ** (-q / 10)

        def fixedDiff(q):
            return q / self.maxQualityScore

        quality_scores = []
        for record in SeqIO.parse(file_path, "fastq"):
            quality_scores.append(record.letter_annotations["phred_quality"])

        # Convert quality scores to float
        quality_float = np.array(quality_scores, dtype=np.float32)
        self.maxQualityScore = np.max(quality_float)
        if mode == "Probability":
            quality_float = probability_helper(quality_float)
        elif mode == "qualityScore":
            pass
        elif mode == "FixedDiff":
            quality_float = fixedDiff(quality_float)

        print("Quality Score Range: ", np.max(quality_float), np.min(quality_float))
        print(quality_float[0])

        # Write to binary file
        with open(output_path, 'wb') as f:
            quality_float.tofile(f)

    def error_calculator(self):
        """
        Calculate the Peak Signal-to-Noise Ratio (PSNR) between self.rawQuality and self.decompressQuality.

        Returns:
        float: The PSNR value.
        """
        # Check if both matrices have the same shape
        if self.rawQuality.shape != self.decompressQuality.shape:
            raise ValueError("Both matrices must have the same shape")

        if np.max(self.decompressQuality) <= 10 or np.min(self.decompressQuality) < 0:
            raise ValueError("self.decompressQuality must have max value > 10 and min value >= 0")

        mse = np.mean((self.rawQuality - self.decompressQuality) ** 2)
        psnr = 10 * np.log10((self.maxQualityScore ** 2) / mse)

        convert_probability = np.vectorize(self.QtoP)
        rawP = convert_probability(self.rawQuality)
        decompressP = convert_probability(self.decompressQuality)
        mse_p = np.mean((rawP - decompressP) ** 2)
        max_pixel_value_p = np.max(rawP)
        psnr_p = 10 * np.log10((max_pixel_value_p ** 2) / mse_p)
        print("Quality Score PSNR: " + str(psnr))
        print("Quality Score MSE: " + str(mse))
        print("Probability PSNR: " + str(psnr_p))
        print("Probability MSE: " + str(mse_p))
        return psnr, mse, psnr_p, mse_p



"""
a = QualityConverter()
# a.fastq_writer("/Users/kurtyang/PycharmProjects/DNA_Compression/FastQ/ERR103405_2.fastq", "/Users/kurtyang/PycharmProjects/DNA_Compression/FastQ_bin/ERR103405_2_F.bin", mode="FixedDiff")

a.fastq_loader("/Users/kurtyang/PycharmProjects/DNA_Compression/FastQ/ERR103405_2.fastq")
# a.fastq_loader("/Users/kurtyang/PycharmProjects/DNA_Compression/FastQ/ERR103405_QualComp_4_2.fastq", type="Decompressed")
a.decompress_loader("/Users/kurtyang/PycharmProjects/DNA_Compression/FastQ_bin/ERR103405_2_F.bin.sz", mode="FixedDiff")
print(a.rawQuality.shape)
print(a.decompressQuality.shape)
# print(a.rawQuality[1] - a.decompressQuality[1])
print(a.rawQuality[1])
print(a.decompressQuality[1])
print(a.rawQuality[2] - a.decompressQuality[2])
print(a.rawQuality[3] - a.decompressQuality[3])
print(a.rawQuality[4] - a.decompressQuality[4])

unique_values = np.unique(a.decompressQuality)
unique_diff = np.unique((a.decompressQuality - a.rawQuality))
print("Range: ", unique_diff.max(), " ", unique_diff.min())

print("Unique Value: ", unique_values)
print("Unique Difference: ", unique_diff)

# print(a.decompressQuality[2])

a.error_calculator()
"""
