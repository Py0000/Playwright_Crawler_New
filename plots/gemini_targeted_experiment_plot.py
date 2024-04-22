
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the dataset
df = pd.read_excel(os.path.join('plots', 'data_sheets', 'Target_Experiment_Results.xlsx'))

# Filter out rows for 0-shot and sort by '# Samples'
df_zero_shot = df[df['Mode'] == '0-shot'].sort_values('# Samples', ascending=False)

# Set color for each type
colors = {'BOTH': '#58D68D', 'SS': '#3498DB', 'HTML': '#F1C40F'}

plt.figure(figsize=(20, 10)) 
bar_width = 0.25
positions = np.arange(len(df_zero_shot['Brand'].unique()))
offsets = {'BOTH': -bar_width, 'SS': 0, 'HTML': bar_width}

for brand_idx, brand in enumerate(df_zero_shot['Brand'].unique()):
    for t in ['BOTH', 'SS', 'HTML']:
        brand_type_data = df_zero_shot[(df_zero_shot['Brand'] == brand) & (df_zero_shot['Type'] == t)]
        if not brand_type_data.empty:
            plt.bar(positions[brand_idx] + offsets[t], brand_type_data['Accuracy'].values[0] * 100, 
                    color=colors[t], width=bar_width, label=t if brand_idx == 0 else "")

# Adjust ticks and labels

plt.xticks(positions, df_zero_shot['Brand'].unique(), rotation=80, fontsize=20)
plt.yticks(fontsize=20)
plt.xlabel('Brand', fontsize=20)
plt.ylabel('Accuracy (%)', fontsize=20)

# Add legend and adjust plot
plt.legend(fontsize=18, loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=3)
plt.ylim(bottom=0)
plt.tight_layout()
plt.grid(axis='y', linestyle='--', color="grey", alpha=0.6)

# Save the figure
plt.savefig(os.path.join('plots', 'figures', "target_brand_gemini.png"))
plt.show()
