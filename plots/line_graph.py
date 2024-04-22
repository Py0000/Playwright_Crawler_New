import os
import matplotlib.pyplot as plt
import utils.constants as Constants

months = Constants.MONTHS
# values = [70.12, 71.56, 64.39] # Fp
values = [73.79, 73.22, 71.94] # Obfuscation

# Plotting the line graph
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(months, values, marker='o', color='blue')  # 'o' for circle markers, line in blue

# Adjusting x and y labels and limits
ax.set_xlabel('Month', fontsize=14)
ax.set_ylabel('Percentage (%)', fontsize=14)
ax.set_ylim([0, 100])  # Y-axis from 0 to 100
ax.yaxis.grid(color='gray', linestyle='dashed', alpha=0.3)
ax.xaxis.grid(color='gray', linestyle='dashed', alpha=0.3)

ax.tick_params(axis='both', which='major', labelsize=12)

plt.tight_layout()
plt.savefig(os.path.join('plots', 'figures', 'obf_trend.png'))
