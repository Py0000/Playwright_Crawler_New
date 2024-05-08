import matplotlib.pyplot as plt

# Data for the months and their corresponding values
months = ['Oct', 'Nov', 'Dec']
values = [73.79, 73.22, 71.94]

# Plotting the line graph
plt.figure(figsize=(8, 5))
plt.plot(months, values, marker='o', linestyle='-', color='blue')
plt.ylim(bottom=0, top=100)
plt.xlabel('Month')
plt.ylabel('Percentage (%)')
plt.grid(True)
plt.savefig('obfuscation_phishing.png')
plt.show()