import argparse
import os
from collections import defaultdict

class DuplicateChecker:
    def init(self):
        return 
    
    def check_for_duplicates(self, month_folder_path):
        month_folders = ["Oct", "Nov", "Dec"]

        # Dictionary to map ZIP folder names (SHA-256 hashes) to a list of dates they appear on
        zip_occurrences = defaultdict(list)
        
        for month in month_folders:
            month_path = os.path.join(month_folder_path, month)
            for dataset_folder in os.listdir(month_path):
                complete_dataset_path = os.path.join(month_path, dataset_folder, dataset_folder, dataset_folder, "complete_dataset")
                for zip_folder in os.listdir(complete_dataset_path):
                    zip_folder_path = os.path.join(complete_dataset_path, zip_folder)
                    if zip_folder_path.endswith(".zip"):
                        # Add the date to the list of occurrences for this ZIP folder
                        zip_occurrences[zip_folder].append(dataset_folder.replace("dataset_", ""))
        
        with open(os.path.join("analyzer", "duplicate", "duplicate_zip_folders.txt"), "w") as file:
            for zip_name, dates in zip_occurrences.items():
                if len(dates) > 1:  # More than one occurrence means it's a duplicate
                    file.write(f"Duplicate ZIP folder: {zip_name} found on dates: {dates}\n")
        



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    parser.add_argument("dataset_path", help="Dataset Path")
    args = parser.parse_args()

    checker = DuplicateChecker()
    checker.check_for_duplicates(args.dataset_path)
