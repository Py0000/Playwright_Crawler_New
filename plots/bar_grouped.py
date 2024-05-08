import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Step 1: Load the CSVs into DataFrames
# You would replace 'file1.csv', 'file2.csv', etc. with your actual file paths
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

for df in [benign, less_popular, phishing, no_ref, bef]:
    total_links = df['# external resources'] + df['# internal resources']
    df['Percentage of Internal resources'] = df['# internal resources']  / total_links * 100
    df['Percentage of External resouces'] = df['# external resources']  / total_links * 100

# Step 2: Add a group identifier column
phishing['Group'] = 'Phishing\n(Ref-After)'
benign['Group'] = 'Benign'
less_popular['Group'] = 'Less\nPopular'
no_ref['Group'] = 'Phishing\n(No Ref-After)'
bef['Group'] = 'Phishing\n(Ref-Before)'

# Step 3: Concatenate all DataFrames
combined_df = pd.concat([benign, less_popular, phishing, no_ref, bef])

# Reordering the DataFrame based on the group
combined_df.sort_values('Group', inplace=True)

# Assuming you want to plot the same columns as in your previous question
columns_to_plot = ['Percentage of Internal resources', 'Percentage of External resouces']

# Set the positions and width for the bars
positions = np.arange(len(combined_df['Group'].unique()))
bar_width = 0.15

# Step 4: Plotting the grouped bar chart
fig, ax = plt.subplots(figsize=(12, 8))

for i, col in enumerate(columns_to_plot):
    ax.bar(positions + i * bar_width, combined_df.groupby('Group')[col].mean(), bar_width, label=col)

# Adding labels and title
ax.set_ylabel('Percentage', fontsize=20)
ax.tick_params(axis='x', labelsize=20)
ax.tick_params(axis='y', labelsize=20)
ax.set_xticks(positions + bar_width / 2 * (len(columns_to_plot) - 1))
ax.set_xticklabels(combined_df['Group'].unique())

# Adding a legend
ax.legend(fontsize=20)

plt.grid(True)
# Display the plot
plt.savefig('html_resources.png')

