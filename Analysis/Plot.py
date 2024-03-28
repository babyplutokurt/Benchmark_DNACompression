import pandas as pd
import matplotlib.pyplot as plt

# Assuming the correct file path is to a CSV file, not a .py file
file_path = '/home/tus53997/Benchmark_DNACompression/Analysis/metric.csv'  # Adjust the file path as necessary


# Plotting function
def plot_scatter(x, y, labels, xlabel, ylabel, title):
    plt.figure(figsize=(20, 20))  # Set the figure size

    # Create a scatter plot for each point and annotate it with its label
    for xi, yi, label in zip(x, y, labels):
        plt.scatter(xi, yi, label=label)
        plt.text(xi, yi, f' {label}', ha='right', va='bottom')
    plot_name = '/home/tus53997/Benchmark_DNACompression/plots/' + xlabel + '_' + ylabel + '.jpg'
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True)
    plt.xlim(0, max(x) + 1)
    plt.ylim(0, max(y) + 1)
    plt.legend(loc='upper right', fontsize='small', ncol=2, title="Job Names")
    plt.savefig(plot_name)
    # plt.show()

def main():
    df = pd.read_csv(file_path)
    ratios = df['Ratio']
    job_names = df['Job Name']
    plot_scatter(ratios, df['Quality Score PSNR'], job_names, 'Ratio', 'Quality Score PSNR', 'Ratio vs Quality Score PSNR')
    plot_scatter(ratios, df['Quality Score MSE'], job_names, 'Ratio', 'Quality Score MSE', 'Ratio vs Quality Score MSE')
    plot_scatter(ratios, df['Probability PSNR'], job_names, 'Ratio', 'Probability PSNR', 'Ratio vs Probability PSNR')
    plot_scatter(ratios, df['Probability MSE'], job_names, 'Ratio', 'Probability MSE', 'Ratio vs Probability MSE')


if __name__ == "__main__":
    main()


