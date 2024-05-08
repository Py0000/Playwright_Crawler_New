import matplotlib.pyplot as plt
import pandas as pd

column = '# stylesheets'

# Replace with your actual data paths
phishing_data_path = 'html_summary.csv'
benign_data_path = 'html_summary_benign.csv'
less_popular_data_path = 'html_summary_101000_105000.csv'
no_ref_data_path = 'html_summary_no_red.csv'
bef_data_path = 'html_summary_bef.csv'

# Load the datasets
phishing = pd.read_csv(phishing_data_path)
benign = pd.read_csv(benign_data_path)
less_popular = pd.read_csv(less_popular_data_path)
no_ref = pd.read_csv(no_ref_data_path)
bef = pd.read_csv(bef_data_path)

# Extract the 'Total' column from each dataset
phishing_counts = phishing[column]
benign_counts = benign[column]
less_popular_counts = less_popular[column]
no_ref_counts = no_ref[column]
bef_counts = bef[column]

# Combine the data into a list
data = [benign_counts, less_popular_counts, phishing_counts, no_ref_counts, bef_counts]

# Create a box plot and adjust the whiskers to the 5th and 95th percentiles
plt.figure(figsize=(12, 8))
plt.boxplot(data, labels=['Benign', 'Less Popular', 'Phishing\n(Ref-After)', 'Phishing\n(No Ref-After)', 'Phishing\n(Ref-Before)'], whis=[5, 95], showfliers=False)
# Add labels and title
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.ylabel('# Stylesheets', fontsize=20)
plt.grid(True)
# Display the plot
plt.savefig('html_stylesheets.png')
