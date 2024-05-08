import matplotlib.pyplot as plt
import numpy as np

# Data
categories = ['Precision', 'Recall', 'Accuracy']
phishing = [97.15, 99.69, 96.68,]
popular = [92.23, 99.06, 91.43]
less_popular = [96.05, 92.01, 88.66]


# Set the width of the bars
bar_width = 0.25

# Set the position of the bars on the x-axis
r1 = np.arange(len(phishing))
r2 = [x + bar_width for x in r1]
r3 = [x + bar_width for x in r2]
#r4 = [x + bar_width for x in r3]
#r5 = [x + bar_width for x in r4]
# Create the bars

plt.figure(figsize=(12, 8))
plt.bar(r1, popular, width=bar_width, label='GeminiPro (Both)', color="green")
plt.bar(r2, less_popular, width=bar_width, label='GeminiPro (SS)', color="blue")
plt.bar(r3, phishing, width=bar_width, label='GeminiPro (HTML)', color="pink")
#plt.bar(r4, no_ref, width=bar_width, label='Phishing (No Ref-After)', color="orange")
#plt.bar(r5, bef, width=bar_width, label='Phishing (Ref-Before)', color="pink")

# Add labels
#plt.xlabel('Met', fontsize=24)
plt.ylabel('Percentage (%)', fontsize=24)
plt.xticks([r + bar_width for r in range(len(phishing))], fontsize=0)
plt.yticks(fontsize=24)
plt.ylim(top=100)
# Create legend & Show graphic
plt.legend(fontsize=24)
plt.grid(axis='y', linestyle='--', color="grey", alpha=0.6)
plt.gca().set_axisbelow(True)
plt.show()
plt.savefig("gemini_pro.png")
