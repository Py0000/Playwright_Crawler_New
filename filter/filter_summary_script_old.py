from datetime import datetime
import json
import os
import pandas as pd

def parse_date(date):
    date_obj = datetime.strptime(date, '%d%m%y')
    return date_obj.strftime('%d %b %Y')

def extract_info_from_dataset_log(root_dir):
    FILTER_LOG_FOLDER = 'filter_logs'
    DATASET_FOLDER_IDENTIFIER = 'dataset_'
    data = []

    for root, dirs, _ in os.walk(root_dir):
        for dir_name in dirs:
            if dir_name.startswith(DATASET_FOLDER_IDENTIFIER) and os.path.isdir(os.path.join(root, dir_name, dir_name)):
                date = dir_name.split('_')[1]  # Extract the date part from the folder name
                stats_path = os.path.join(root, dir_name, FILTER_LOG_FOLDER, f'{date}_statistics.json')
                print(stats_path)
                print(os.path.isfile(stats_path))
                if os.path.isfile(stats_path):
                    with open(stats_path, 'r') as file:
                        stats = json.load(file)
                        date = parse_date(date)
                        stats['Date'] = date # Add the date to the stats dictionary
                        data.append(stats) # Add the date and the rest of the stats to our data list.
    
    return data

def generate_csv(data):
    if data:
        df = pd.DataFrame(data)
        expected_columns = [
            "Date",
            "Total number of dataset",
            "Number of complete dataset",
            "Number of complete dataset with status code 200",
            "Number of complete dataset with other status codes",
            "Number of both (self ref & no ref) faulty dataset",
            "Number of self ref only faulty dataset",
            "Number of no ref only faulty dataset"
        ]
            
        # Reorder the columns according to the expected order
        df = df[expected_columns]

        output_csv_path = 'consolidated_filter_statistics.csv'
        df.to_csv(output_csv_path, index=False)



if __name__ == '__main__':
    root_dir = "filtered_test"
    data = extract_info_from_dataset_log(root_dir)
    generate_csv(data)

