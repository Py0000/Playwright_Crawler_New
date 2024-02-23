import argparse
import hashlib
import os
from collections import defaultdict
from zipfile import ZipFile

class DuplicateChecker:
    def __init__(self):
        self.month_folders = ["Oct", "Nov", "Dec"]
        return 
    
    def check_for_duplicates_url(self, month_folder_path):
        # Dictionary to map ZIP folder names (SHA-256 hashes) to a list of dates they appear on
        zip_occurrences = defaultdict(list)
        
        for month in self.month_folders:
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
    

    def check_for_duplicates_html(self, month_folder_path):
        unique_hashes = set()

        # Dictionary to map ZIP folder names (SHA-256 hashes) to a list of dates they appear on
        zip_occurrences = defaultdict(list)
        new = 0
        dup = 0
        for month in self.month_folders:
            month_path = os.path.join(month_folder_path, month)
            for dataset_folder in os.listdir(month_path):
                complete_dataset_path = os.path.join(month_path, dataset_folder, dataset_folder, dataset_folder, "complete_dataset")
                for zip_folder in os.listdir(complete_dataset_path):
                    zip_folder_path = os.path.join(complete_dataset_path, zip_folder)
                    if zip_folder_path.endswith(".zip"):
                        with ZipFile(zip_folder_path, 'r') as zip_ref:
                            html_file_paths = [file for file in zip_ref.namelist() if "self_ref/html_script_aft.html" in file]
                            with zip_ref.open(html_file_paths[0]) as html_file:
                                content = html_file.read()
                                content_hash = hashlib.sha256(content).hexdigest() #Hash the html content

                                if content_hash in unique_hashes: #If hash already appeared before, means the content is duplicated. 
                                    print(f"Duplicate found in {zip_folder_path}")
                                    zip_occurrences[dataset_folder.replace("dataset_", "")].append(zip_folder)
                                    dup += 1
                                else:
                                    unique_hashes.add(content_hash)
                                    new += 1
        
        print(f"\n\nNew: {new}\nDup: {dup}")
        
        with open(os.path.join("analyzer", "duplicate", "html_duplicate_zip_folders.txt"), "w") as file:
            for dates, zip_name in zip_occurrences.items():
                if len(zip_name) > 0:  # More than one occurrence means it's a duplicate
                    file.write(f"\nDuplicate for: {dates}: {zip_name}\n")
                                
        



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    parser.add_argument("dataset_path", help="Dataset Path")
    parser.add_argument("mode", help="url or html")
    args = parser.parse_args()

    checker = DuplicateChecker()
    if args.mode == "url":
        checker.check_for_duplicates_url(args.dataset_path)
    elif args.mode == "html":
        checker.check_for_duplicates_html(args.dataset_path)
