import argparse
import json
import os
from urllib.parse import urlparse
import zipfile

from tqdm import tqdm

from utils.file_utils import FileUtils
import utils.constants as Constants

class UrlPortionChecker:
    def __init__(self):
        self.url_counts = {}

    def obtain_url_from_log_file(self, zip_ref):
        log_path = FileUtils.extract_file_path_from_zipped(zip_ref, "self_ref", "log.json")
        url = None
        if log_path:
             with zip_ref.open(log_path) as log_file:
                log_data = FileUtils.read_from_json_zipped_file(log_file)
                url = log_data["Url visited"]
        return url

    def parse_url(self, url):
        parsed_url = urlparse(url)
        normalized = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        return normalized.rstrip('/')

    def scan_directories(self, zip_folder_path, date):
        for zip_file in tqdm(os.listdir(zip_folder_path)):
            if zip_file.endswith(".zip"):
                hash = zip_file.split(".zip")[0]
                zip_path = os.path.join(zip_folder_path, zip_file)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    url = self.obtain_url_from_log_file(zip_ref)
                    if url:
                        parsed_url = self.parse_url(url)
                        if parsed_url in self.url_counts:
                            self.url_counts[parsed_url].append((date, hash, url))
                        else:
                            self.url_counts[parsed_url] = [(date, hash, url)]
    
    def extract_duplicates(self):
        filtered_data = {key: value for key, value in self.url_counts.items() if len(value) > 1}
        print(len(filtered_data))
        return filtered_data

    def obtain_urls_data(self):
        return self.url_counts

    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Check if landing url are similar except for input params")
    parser.add_argument("folder", help="Input the folder that contains the dataset")
    parser.add_argument("result_path", help="Input the folder to store the results")
    args = parser.parse_args()

    if not os.path.exists(args.result_path):
        os.makedirs(args.result_path)

    folders = Constants.PHISHING_FOLDERS_VALIDATED_OCT + Constants.PHISHING_FOLDERS_VALIDATED_NOV + Constants.PHISHING_FOLDERS_VALIDATED_DEC
    url_portion_checker = UrlPortionChecker()
    for folder in folders:
        print(f"Processing {folder}")
        folder_path = os.path.join(args.folder, f"original_dataset_{folder}")
        date = folder
        url_portion_checker.scan_directories(folder_path, date)
    
    data = url_portion_checker.obtain_urls_data()
    full_output = os.path.join(args.result_path, 'full_analysis.json')
    FileUtils.save_as_json_output(full_output, data)

    filtered_data = url_portion_checker.extract_duplicates()
    dup_output = os.path.join(args.result_path, 'dup_only_analysis.json')
    FileUtils.save_as_json_output(dup_output, filtered_data)


    