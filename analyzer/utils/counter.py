import argparse
import os
import re
from analyzer.utils import file_utils

class Counter:
    def __init__(self, type):
        self.accumulated = 0
        self.type = type
        self.count_txt_file = os.path.join("analyzer", "utils", f"dataset_count_{self.type}.txt")
    

    def get_count_of_one_day_dataset(self, dataset_path, date):
        subfolders = ["both", "no_ref", "self_ref"]

        if "zip" in dataset_path:
            dataset_path = file_utils.extract_zipfile(dataset_path)
        
        parent_folder_path = os.path.join(dataset_path, f'dataset_{date}', f'dataset_{date}', 'complete_dataset')
        type_path = os.path.join(parent_folder_path, self.type)

        zip_counts = {subfolder: 0 for subfolder in subfolders}
        for subfolder in subfolders:
            folder_path = os.path.join(type_path, subfolder)
            files = os.listdir(folder_path)
            zip_counts[subfolder] = sum(1 for file in files if file.endswith(".zip"))

        total_count = sum(zip_counts.values())
        zip_counts["Total"] = total_count
        self.accumulated = self.accumulated + total_count

        print(date, zip_counts)
        with open(self.count_txt_file, 'a') as file:
            file.write(f"{str(date)}\n")
            for subfolder, count in zip_counts.items():
                file.write(f"Number of ZIP files in {subfolder}: {count}\n")
            file.write("\n")
        
    def save_accumulated(self):
        print(self.accumulated)
        with open(self.count_txt_file, 'a') as file:
            file.write(f"Accumulated: {self.accumulated}")
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    parser.add_argument("dataset_path", help="Dataset Path")
    parser.add_argument("type", help="blank_pages or blocked")
    args = parser.parse_args()

    months = ["Oct", "Nov", "Dec"]

    counter = Counter(args.type)
    for month in months:
        month_folder_path = os.path.join(args.dataset_path, month)
        folders = os.listdir(month_folder_path)

        for folder in folders:
            date = re.search(r"dataset_(\d+)", folder).group(1)
            counter.get_count_of_one_day_dataset(os.path.join(month_folder_path, folder), date)
    
    counter.save_accumulated()


