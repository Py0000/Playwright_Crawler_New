import pandas as pd
import matplotlib.pyplot as plt

column = "# Hidden Elements"

# Load the datasets
phishing_data_path = 'html_summary.csv'
benign_data_path = 'html_summary_benign.csv'
less_popular_data_path = 'html_summary_101000_105000.csv'
no_ref_data_path = 'html_summary_no_red.csv'
bef_data_path = 'html_summary_bef.csv'

phishing = pd.read_csv(phishing_data_path)
benign = pd.read_csv(benign_data_path)
less_popular = pd.read_csv(less_popular_data_path)
no_ref = pd.read_csv(no_ref_data_path)
bef = pd.read_csv(bef_data_path)

phishing_counts = phishing[column].value_counts(normalize=True) * 100
benign_counts = benign[column].value_counts(normalize=True) * 100
less_popular_counts = less_popular[column].value_counts(normalize=True) * 100
no_ref_counts = no_ref[column].value_counts(normalize=True) * 100
bef_counts = bef[column].value_counts(normalize=True) * 100

colors = ['green', 'blue', 'red', 'orange', 'pink']

df = pd.DataFrame({
    'Phishing (Ref-After)': phishing_counts,
    'Benign': benign_counts,
    'Less Popular': less_popular_counts,
    'Phishing (No Ref-After)': no_ref_counts,
    'Phishing (Ref-Before)': bef_counts
}).fillna(0)

"""
threshold = 0.25
df_filtered = df[(df['Phishing'] > threshold) | (df['Benign'] > threshold) | (df['Less Popular'] > threshold)]
df = df_filtered
"""
"""
df['Total'] = df.sum(axis=1)
df_sorted = df.sort_values('Total', ascending=False)
df_sorted = df_sorted.drop(columns=['Total'])
df = df_sorted
"""

ax = df.plot(kind='bar', figsize=(14, 7), width=0.7, color=colors)
ax.set_ylabel('Percentage', fontsize=16)
ax.set_xlabel('# Hidden Elements', fontsize=16)
plt.xticks(rotation=45, ha='right',  fontsize=14)
plt.legend(fontsize=12)
plt.tight_layout()
plt.grid(axis='y', linestyle='--', color="grey", alpha=0.6)
plt.gca().set_axisbelow(True)
plt.show()
plt.savefig("html_hidden.png")