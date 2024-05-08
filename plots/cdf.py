import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Function to calculate CDF
def compute_cdf(data):
    # Count the number of values greater than or equal to 3
    values_greater_equal_3 = data
    # Calculate the CDF
    sorted_data = np.sort(values_greater_equal_3)
    yvals = np.arange(len(sorted_data)) / float(len(sorted_data) - 1)
    return sorted_data, yvals

# File paths
phishing_data_path = 'html_summary.csv'
benign_data_path = 'html_summary_benign.csv'
less_popular_data_path = 'html_summary_101000_105000.csv'
no_ref_data_path = 'html_summary_no_red.csv'
bef_data_path = 'html_summary_bef.csv'

files = [benign_data_path, less_popular_data_path, phishing_data_path, no_ref_data_path, bef_data_path]
colors = ['green', 'blue', 'red', 'orange', 'pink']  # Colors for the lines
labels = ['Popular', 'Less Popular', 'Phishing (Ref-After)', 'Phishing (No Ref-After)', 'Phishing (Ref-Before)']  # Labels for the legend

# Plotting the CDF for each CSV file
plt.figure()
for file, color, label in zip(files, colors, labels):
    try:
        df = pd.read_csv(file, encoding='utf-8', low_memory=False)
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file, encoding='ISO-8859-1', low_memory=False)
        except UnicodeDecodeError:
            df = pd.read_csv(file, encoding='cp1252', low_memory=False)
    sorted_data, yvals = compute_cdf(df['# Hidden Elements'])
    plt.plot(sorted_data, yvals, label=label, color=color)

# Customize the plot
plt.grid(True)
plt.legend()
plt.xlabel('# Hidden Elements')
plt.xlim(left=0)  # Set x-axis to start at 0
plt.ylim(bottom=0)  # Set y-axis to start at 0

# Show the plot
plt.show()
plt.savefig("html_hidden.png")