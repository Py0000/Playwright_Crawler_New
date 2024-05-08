import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

# Load the CSV files
csv1 = pd.read_csv('Certificate_info_summary.csv')
csv2 = pd.read_csv('Certificate_info_summary_benign.csv')
csv3 = pd.read_csv('Certificate_info_summary_less_pop_benign.csv')

# Calculate percentages for Certificate Issuer
issuer_counts_1 = csv1['Certificate Issuer'].value_counts(normalize=True)
issuer_counts_2 = csv2['Certificate Issuer'].value_counts(normalize=True)
issuer_counts_3 = csv3['Certificate Issuer'].value_counts(normalize=True)

# Bar chart for Certificate Issuer percentages
plt.figure(figsize=(10, 6))
plt.bar(issuer_counts_1.index, issuer_counts_1.values, alpha=0.5, label='CSV 1')
plt.bar(issuer_counts_2.index, issuer_counts_2.values, alpha=0.5, label='CSV 2')
plt.bar(issuer_counts_3.index, issuer_counts_3.values, alpha=0.5, label='CSV 3')
plt.ylabel('Percentage')
plt.title('Certificate Issuer Percentage by CSV')
plt.legend()
plt.xticks(rotation=90)
plt.tight_layout()
plt.ylim(bottom=0)
plt.show()
plt.savefig('cert_issuer.png')

# Calculate percentages for Signature Algorithm
signature_counts_1 = csv1['Certificate Signature Algorithm'].value_counts(normalize=True)
signature_counts_2 = csv2['Certificate Signature Algorithm'].value_counts(normalize=True)
signature_counts_3 = csv3['Certificate Signature Algorithm'].value_counts(normalize=True)

# Bar chart for Signature Algorithm percentages
plt.figure(figsize=(10, 6))
plt.bar(signature_counts_1.index, signature_counts_1.values, alpha=0.5, label='CSV 1')
plt.bar(signature_counts_2.index, signature_counts_2.values, alpha=0.5, label='CSV 2')
plt.bar(signature_counts_3.index, signature_counts_3.values, alpha=0.5, label='CSV 3')
plt.ylabel('Percentage')
plt.title('Certificate Signature Algorithm Percentage by CSV')
plt.legend()
plt.xticks(rotation=90)
plt.tight_layout()
plt.ylim(bottom=0)
plt.show()
plt.savefig('sign_algo.png')

# Plot CDF for Certificate Valid Duration
plt.figure(figsize=(10, 6))
for data, label, color in zip([csv1['Certificate Valid Duration'], csv2['Certificate Valid Duration'], csv3['Certificate Valid Duration']], ['CSV 1', 'CSV 2', 'CSV 3'], ['blue', 'orange', 'green']):
    sns.ecdfplot(data, label=label, color=color)
plt.ylabel('CDF')
plt.xlabel('Certificate Valid Duration (Days)')
plt.title('Certificate Valid Duration CDF by CSV')
plt.legend()
plt.grid(True)
plt.xlim(left=0)  # Start x-axis at 0
plt.ylim(bottom=0)  # Start y-axis at 0
plt.show()
plt.savefig('valid duration.png')