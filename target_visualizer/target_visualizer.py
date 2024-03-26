import argparse
from datetime import datetime
import pandas as pd 
import matplotlib.pyplot as plt

class TargetVisualizer:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    
    def parse_date(self, date):
        if isinstance(date, float) and pd.isna(date):
            return pd.NaT
        
        date = str(date)
        date = date.replace('st', '').replace('nd', '').replace('rd', '').replace('th', '')
        try:
            return datetime.strptime(date, '%d %b %Y')
        except:
            return pd.NaT


    def set_common_settings_for_plot(self, x_label, y_label):
        plt.figure(figsize=(50, 25)) # Set the figure size
        plt.xticks(rotation=90) # Rotate the x-axis labels to show them vertically
        plt.xlabel(x_label) # Set the x-axis label
        plt.ylabel(y_label) # Set the y-axis label 
        plt.title(f'Targeted Brands for week {self.start_date} to {self.end_date}') # Set the title of the chart
        plt.tight_layout(rect=[0, 0.1, 1, 1]) # Adjust the layout to fit everything nicely
        plt.subplots_adjust(bottom=0.15)
        plt.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray', axis='y')


    def save_plot(self, plot_output_name):
        plt.savefig(plot_output_name)
        plt.close()

    
    def get_targeted_brand_from_sheet(self, file_name):
        df = pd.read_excel(file_name, engine='openpyxl')

        # Convert the 'Date' column to datetime
        df['Date (of Dataset)'] = pd.to_datetime(df['Date (of Dataset)'].apply(self.parse_date))

        # Filter the dataFrame to include only the specified date range
        start_date = datetime.strptime(self.start_date, '%d%m%y').strftime('%Y-%m-%d')
        end_date = datetime.strptime(self.end_date, '%d%m%y').strftime('%Y-%m-%d')
        mask = (df['Date (of Dataset)'] >= start_date) & (df['Date (of Dataset)'] <= end_date)
        
        # Only include those targets that are deemed as phishing after VirusTotal validation (>4) and manually verified
        mask &= (df['Final Verdict'] == 'Yes')
        filtered_df = df.loc[mask]

        # Extract targeted Brandfrom the filtered DataFrame
        brands = filtered_df['Targeted Brand / Categories']

        # Count the occurrences of each brand/category
        brand_counts = brands.value_counts()

        return brand_counts


    def generate_frequency_diagram(self, data_counts):
        self.set_common_settings_for_plot("Targeted Brand", "Frequency")
        
        # Create a bar chart
        plt.bar(data_counts.index, data_counts.values)

        # Save the diagram
        output_file = f"target_{self.start_date}_to_{self.end_date}.png"
        self.save_plot(output_file)


    def generate_percentage_diagram(self, data_counts):
        self.set_common_settings_for_plot('Targeted Brand', '%')

        # Calculate the percentages
        total_count = data_counts.sum()
        percentages = (data_counts / total_count) * 100

        # Create a bar chart
        plt.bar(percentages.index, percentages.values)

        # Include the total count 
        plt.text(x=0.5, y=0.95, s=f"Total Count: {total_count}", 
                ha='center', va='top', transform=plt.gca().transAxes)
        
        # Save the diagram
        output_file = f"target_percentage_{self.start_date}_to_{self.end_date}.png"
        self.save_plot(output_file)



    def generate_empirical_cdf_diagram(self, data_counts):
        self.set_common_settings_for_plot('Targeted Brand', 'CDF')

        # Convert the series to a DataFrame
        df = data_counts.reset_index()
        df.columns = ['Brand', 'Count']

        # Sort the DataFrame by count
        df = df.sort_values(by='Count', ascending=False)

        # Calculate the cumulative sum of the counts
        df['Cumulative'] = df['Count'].cumsum()
        df['CDF'] = df['Cumulative'] / df['Cumulative'].max()

        # Plotting
        plt.step(df['Brand'], df['CDF'], where='post')

        # Save the diagram
        output_file = f"target_cdf_{self.start_date}_to_{self.end_date}.png"
        self.save_plot(output_file)


    def visualize(self, file_name):
        data_counts = self.get_targeted_brand_from_sheet(file_name)
        self.generate_frequency_diagram(data_counts)
        self.generate_percentage_diagram(data_counts)
        self.generate_empirical_cdf_diagram(data_counts)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    parser.add_argument("excel_file_path", help="Name of the excel file")
    parser.add_argument("start_date", help="Start Date")
    parser.add_argument("end_date", help="End Date")
    args = parser.parse_args()

    file_name = args.excel_file_path 
    start_date = args.start_date
    end_date = args.end_date

    target_visualizer = TargetVisualizer(start_date, end_date)
    target_visualizer.visualize(file_name)
