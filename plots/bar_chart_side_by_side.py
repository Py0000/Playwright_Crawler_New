import os
import matplotlib.pyplot as plt
import numpy as np

# Define the categories and scores for each
categories = ['GeminiPro (Both)', 'GeminiPro (SS)', 'GeminiPro (HTML)']
precision = [97.15, 92.23, 96.05]
recall = [99.69, 99.06, 92.01]
accuracy = [96.68, 91.43, 88.66]

# Define the x location for the groups
x = np.arange(len(categories))

# Define the width of the bars
bar_width = 0.25

# Plotting the bars
fig, ax = plt.subplots(figsize=(12, 8))

bar1 = ax.bar(x - bar_width, precision, bar_width, label='Precision', color='#3498DB')
bar2 = ax.bar(x, recall, bar_width, label='Recall', color='#58D68D')
bar3 = ax.bar(x + bar_width, accuracy, bar_width, label='Accuracy', color='#F1C40F')

# Adding the numerical scores above the bars
for bar in bar1 + bar2 + bar3:
    height = bar.get_height()
    ax.annotate(f'{height:.2f}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha='center', va='bottom')

# Adding labels and title
ax.set_xlabel('Category', fontsize=18, labelpad=20)
ax.set_ylabel('Scores (%)', fontsize=18)
ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=3, fontsize=13)
plt.grid(axis='y', linestyle='--', color="grey", alpha=0.6)

# Show the plot
plt.xticks(rotation=0, fontsize=16)
plt.tight_layout()  # Adjust the plot to ensure everything fits without overlapping
plt.savefig(os.path.join('plots', 'figures', 'gemini_metrics_bar.png'))
