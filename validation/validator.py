import argparse
import json
import os
import zipfile

from validation.url_scanner import UrlScanner
from validation.html_scanner import HtmlScanner


from utils.file_utils import FileUtils
from validation.utils import ValidationUtils

class Validator:
    def __init__(self, api_key, is_revalidate):
        self.api_key = api_key
        self.is_revalidate = is_revalidate
        self.url_scanner = UrlScanner()
        self.html_scanner = HtmlScanner()
    
    def read_url_from_previously_validated_list(self, url_list_txt):
        with open(url_list_txt, 'r') as file:
            url_list = [line.strip() for line in file if line.strip()]
        return dict.fromkeys(url_list)

    def extract_url_for_scanning(self, original_dataset_path):
        url_to_file_hash_dict = {}
        for folder in os.listdir(original_dataset_path):
            folder_path = os.path.join(original_dataset_path, folder)
            try:
                log_path = FileUtils.extract_file_path_from_zipped(folder_path, "self_ref", "log.json")
                if log_path:
                    with open(log_path, 'r') as file:
                        data = json.load(file)
                    url = data["Provided Url"]
                    hash_value = data["Provided Url Hash (in SHA-256)"]
                    url_to_file_hash_dict[url] = hash_value
            except Exception as e:
                print(f"Error for {folder}: {e}")
        
        return url_to_file_hash_dict
    
    def extract_html_files_for_scanning(self, original_dataset_path):
        html_data = {}
        for folder in os.listdir(original_dataset_path):
            folder_path = os.path.join(original_dataset_path, folder)
            try:
                html_path = FileUtils.extract_file_path_from_zipped(folder_path, "self_ref", "html_script_aft.html")
                if html_path:
                    with open(html_path, 'r', encoding='utf-8') as file:
                        html_content = file.read()
                    
                    files = {
                        'file': ('filename.html', html_content)
                    }
                    html_data[os.path.basename(folder)] = files
            except Exception as e:
                print(f"Error for {folder}: {e}")

        return html_data
            

    def validate_url(self, original_dataset_path, date, url_text):
        if self.is_revalidate:
            url_to_file_hash_dict = self.read_url_from_previously_validated_list(url_text)
        else:
            url_to_file_hash_dict = self.extract_url_for_scanning(original_dataset_path)

        self.url_scanner.get_url_validation_result(url_to_file_hash_dict, date, self.api_key)
    
    def validate_html(self, original_dateset_path, date):
        html_data_list = self.extract_html_files_for_scanning(original_dateset_path)
        self.html_scanner.get_html_validation_result(html_data_list, date, self.api_key)
    





if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Validate selected samples using VirusTotal")
    parser.add_argument("original_dataset_folder_path", help="Name of the original dataset folder path")
    parser.add_argument("date", help="Date of dataset")
    parser.add_argument("--is_revalidate", choices=["yes", "no"], default="no", help='Input yes if doing revalidation')
    parser.add_argument("--url_txt", default=None, help='Input txt file if doing revalidation')
    args = parser.parse_args()

    api_key_file = os.path.join('validation', 'virus_total_api_key.txt')
    api_key = ValidationUtils.read_virus_total_api_key(api_key_file)

    is_revalidate = True if args.is_revalidate == "yes" else False
    validator = Validator(api_key, is_revalidate)
    validator.validate_url(args.original_dataset_folder_path, args.date, args.url_txt)
    validator.validate_html(args.original_dataset_folder_path, args.date)


    


