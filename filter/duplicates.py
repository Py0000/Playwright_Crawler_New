

import argparse
import ast
from collections import defaultdict
import hashlib
import os
import re
from zipfile import ZipFile

from tqdm import tqdm

import utils.constants as Constants
from utils.file_utils import FileUtils

class DuplicateChecker:
    def __init__(self):
        pass

    def check_for_duplicates_phishing_url(self, dataset_path):
        # Dictionary to map ZIP folder names (SHA-256 hashes) to a list of dates they appear on
        zip_occurrences = defaultdict(list)

        for month in Constants.MONTHS:
            month_path = os.path.join(dataset_path, month)
            for dataset_folder in tqdm(os.listdir(month_path)):
                complete_dataset_path = os.path.join(month_path, dataset_folder, dataset_folder, dataset_folder, "complete_dataset")
                for zip_folder in tqdm(os.listdir(complete_dataset_path)):
                    zip_folder_path = os.path.join(complete_dataset_path, zip_folder)
                    if zip_folder_path.endswith(".zip"):
                        # Add the date to the list of occurrences for this ZIP folder
                        zip_occurrences[zip_folder].append(dataset_folder.replace("dataset_", ""))

        output_file = os.path.join("filter", "duplicate", "duplicate_zip_folders.txt")
        with open(output_file, "w") as file:
            for zip_name, dates in zip_occurrences.items():
                if len(dates) > 1:  # More than one occurrence means it's a duplicate
                    file.write(f"Duplicate ZIP folder: {zip_name} found on dates: {dates}\n")
        
        return output_file
    
    
    def check_for_duplicates_phishing_html(self, dataset_path):
        # Dictionary to map ZIP folder names (SHA-256 hashes) to a list of dates they appear on
        zip_occurrences = defaultdict(list)
        unique_hashes = set()
        new = 0
        dup = 0

        for month in Constants.MONTHS:
            month_path = os.path.join(dataset_path, month)
            for dataset_folder in tqdm(os.listdir(month_path)):
                complete_dataset_path = os.path.join(month_path, dataset_folder, dataset_folder, dataset_folder, "complete_dataset")
                for zip_folder in tqdm(os.listdir(complete_dataset_path)):
                    if not zip_folder.endswith('.zip'):
                        continue
                    zip_folder_path = os.path.join(complete_dataset_path, zip_folder)
                    with ZipFile(zip_folder_path, 'r') as zip_ref:
                        html_path = FileUtils.extract_file_path_from_zipped(zip_ref, 'self_ref', 'html_script_aft.html')
                        with zip_ref.open(html_path) as html_file:
                            content = html_file.read()
                        content_hash = hashlib.sha256(content).hexdigest() #Hash the html content
                        if content_hash in unique_hashes: #If hash already appeared before, means the content is duplicated.
                            zip_occurrences[dataset_folder.replace("dataset_", "")].append(zip_folder)
                            dup += 1
                        else:
                            unique_hashes.add(content_hash)
                            new += 1
        
        print(f"\n\nNew: {new}\nDup: {dup}")
        output_file = os.path.join("filter", "duplicate", "html_duplicate_zip_folders.txt")
        with open(output_file, "w") as file:
            for dates, zip_name in zip_occurrences.items():
                if len(zip_name) > 0:  # More than one occurrence means it's a duplicate
                    file.write(f"\nDuplicate for: {dates}: {zip_name}\n")
        return output_file
    
    """
    def check_for_duplicates_benign_url(self, dataset_path):
        zip_occurrences = defaultdict(list)
        complete_dataset_path = os.path.join(dataset_path, "complete_dataset")
        for folder in tqdm(os.listdir(complete_dataset_path)):
            if not folder.endswith('.zip'):
                continue
            zip_folder_path = os.path.join(complete_dataset_path, folder)
            zip_occurrences[zip_folder_path].append(dataset_path)
        
        with open(os.path.join("filter", "duplicate", "duplicate_zip_folders_benign.txt"), "w") as file:
            for zip_name, dates in zip_occurrences.items():
                if len(dates) > 1:  # More than one occurrence means it's a duplicate
                    file.write(f"Duplicate ZIP folder: {zip_name} found on dates: {dates}\n")
    
    def check_for_duplicates_benign_url(self, dataset_path):
        # Dictionary to map ZIP folder names (SHA-256 hashes) to a list of dates they appear on
        zip_occurrences = defaultdict(list)
        unique_hashes = set()
        new = 0
        dup = 0

        complete_dataset_path = os.path.join(dataset_path, "complete_dataset")
        for folder in tqdm(os.listdir(complete_dataset_path)):
            if not folder.endswith('.zip'):
                continue
            zip_folder_path = os.path.join(complete_dataset_path, folder)
            with ZipFile(zip_folder_path, 'r') as zip_ref:
                html_path = FileUtils.extract_file_path_from_zipped(zip_ref, 'self_ref', 'html_script_aft.html')
                with zip_ref.open(html_path) as html_file:
                    content = html_file.read()
                content_hash = hashlib.sha256(content).hexdigest() #Hash the html content
                if content_hash in unique_hashes: #If hash already appeared before, means the content is duplicated.
                    zip_occurrences[dataset_path].append(folder)
                    dup += 1
                else:
                    unique_hashes.add(content_hash)
                    new += 1
        
        print(f"\n\nNew: {new}\nDup: {dup}")
        with open(os.path.join("filter", "duplicate", "html_duplicate_zip_folders_benign.txt"), "w") as file:
            for dates, zip_name in zip_occurrences.items():
                if len(zip_name) > 0:  # More than one occurrence means it's a duplicate
                    file.write(f"\nDuplicate for: {dates}: {zip_name}\n")
        """



class DuplicateRemover:
    def __init(self):
        pass

    def get_month_folder_from_date(self, date):
        month_mapping = {
            "10": "Oct",
            "11": "Nov",
            "12": "Dec"
        }

        month_part = date[2:4]
        return month_mapping.get(month_part)
    

    def delete_url_duplicates(self, zip_name, dates_to_delete):
        for date in dates_to_delete:
            month = self.get_month_folder_from_date(date)
            zip_folder_path = os.path.join("datasets", month, f"dataset_{date}", f"dataset_{date}", f"dataset_{date}", "complete_dataset", zip_name)
            os.remove(zip_folder_path)
            print(f"Deleted: {zip_folder_path}")


    def read_and_delete_url_duplicates(self, duplicate_txt_file):
        with open(duplicate_txt_file, "r") as file:
            for line in file:
                # Extract ZIP name and dates
                parts = line.split(" found on dates: ")
                zip_name = parts[0].replace("Duplicate ZIP folder: ", "").strip()
                dates = ast.literal_eval(parts[1].strip())
                # date_to_keep = dates[0]
                dates_to_delete = dates[1:]

                self.delete_url_duplicates(zip_name, dates_to_delete)   
    

    def read_html_duplicates(self, duplicate_txt_file):
        pattern = r'Duplicate for: (\d+): \[([^\]]+)\]'
        with open(duplicate_txt_file, "r") as file:
            content = file.read()
        matches = re.findall(pattern, content)
        date_zip_pairs = {}
        for match in matches:
            date = match[0]
            zip_files_str = match[1]
            zip_files = [zip_file.strip().strip("'\"") for zip_file in zip_files_str.split(', ')]

            date_zip_pairs[date] = zip_files
        
        return date_zip_pairs

    def remove_html_duplicates(self, info):
        for date, zip_folders in info.items():
            month = self.get_month_folder_from_date(date)
            for zip_folder in zip_folders:
                zip_folder_path = os.path.join("datasets", month, f"dataset_{date}", f"dataset_{date}", f"dataset_{date}", "complete_dataset", zip_folder)
                os.remove(zip_folder_path)
                print(f"Deleted: {zip_folder_path}")

    def read_and_delete_html_duplicates(self, duplicate_txt_file):
        date_zip_pairs = self.read_html_duplicates(duplicate_txt_file)
        self.remove_html_duplicates(date_zip_pairs)
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    parser.add_argument("dataset_path", help="Dataset Path")
    parser.add_argument("--phishing_mode", choices=['phishing', 'benign'], default='phishing', help="phishing or benign")
    parser.add_argument("file_type", choices=['url', 'html'], help="url or html")
    args = parser.parse_args()

    checker = DuplicateChecker()
    remover = DuplicateRemover()
    if args.mode == "url":
        output_file_path = checker.check_for_duplicates_phishing_url(args.dataset_path)
        remover.read_and_delete_url_duplicates(output_file_path)
    elif args.mode == "html":
        output_file_path = checker.check_for_duplicates_phishing_html(args.dataset_path)
        remover.read_and_delete_html_duplicates(output_file_path)
    


    



                    
