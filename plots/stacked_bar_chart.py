import os
import matplotlib.pyplot as plt

# Data to plot
domain_categories = ['Benign Top 10k', 'Benign 100k-105k', 'Phishing']
'''
# Fingerprint Values
main_value = [70.24, 89.38, 68.14]
sub_value = [70.24 * (22.11 / 100), 89.38 * (85.64 / 100), 68.14 * (68.81 / 100)]
'''
# Obfuscation Values
main_value = [16.11, 87.98, 76.47]
sub_value = [16.11 * (22.15 / 100), 87.98 * (22.13 / 100), 76.47 * (11.664 / 100)]

# Create a new bar plot
fig, ax = plt.subplots(figsize=(10, 6))

# Plot main bars
bars1 = ax.bar(domain_categories, main_value, color='blue', width=0.3, edgecolor='grey', label='Score < 100')

# Overlay sub bars
bars2 = ax.bar(domain_categories, sub_value, color='orange', width=0.3, edgecolor='grey', label='Score >= 100')

# Add some text for labels and custom x-axis tick labels, etc.
ax.set_xlabel('Domain Category', fontsize=14)
ax.set_ylabel('Percentage (%)', fontsize=14)
ax.set_xticks([r for r in range(len(domain_categories))])
ax.set_xticklabels(domain_categories, fontsize=12)
ax.xaxis.labelpad = 20
ax.set_ylim([0, 100])  # Extend y-axis to 100 for better comparison
ax.yaxis.grid(color='gray', linestyle='dashed')
ax.legend(fontsize=12)

# Adding the data labels for main bars
for bar in bars1:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval - 5, round(yval, 2), ha='center', va='bottom', color='white', weight='bold', fontsize=12)

# Show the figure
plt.tight_layout()
plt.savefig(os.path.join('plots', 'figures', 'obf_graph.png'))
