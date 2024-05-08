import matplotlib.pyplot as plt

# Data for pie chart
labels = ['Chrome 116.0 Win10', 'Chrome 116.0 macOS', 'Edge 116.0 Win10', 
          'Safari 16.5.1 macOS', 'Firefox 117.0 macOS', 'Others (<4% each)']
#sizes = [22.5, 9.8, 7.6, 5.3, 4.9, 49.9] #willshouse stats
sizes = [33.54, 10.39, 8.58, 5.01, 4.87, 35.61] #useragents.me stats

# Define colors for each section
colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0','#ffb3e6']

# Create the pie chart
plt.figure(figsize=(8,6))
patches, texts, autotexts = plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)

# Equal aspect ratio ensures that pie is drawn as a circle.
plt.axis('equal')

for text in texts:
    text.set_fontsize(14)

for autotext in autotexts:
    autotext.set_fontsize(13)

# Show the pie chart
plt.savefig('pop_ua_useragents.png', bbox_inches='tight')
