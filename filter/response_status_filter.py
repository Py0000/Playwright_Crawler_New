
import argparse
import os
import zipfile
import shutil

from tqdm import tqdm
from filter.faulty_data_filter import FaultyDataFilterer
from utils.file_utils import FileUtils

class ResponseStatusFilterer:
    def __init__(self):
        pass

    def consolidate_reponse_status(dataset_directory, date):
        code_200_data = {}
        non_code_200_data = {}

        complete_dataset_full_dir = os.path.join(dataset_directory, "complete_dataset")
        
        for folder in tqdm(os.listdir(complete_dataset_full_dir)):
            if not folder.endswith(".zip"):
                continue

            zip_file_path = os.path.join(complete_dataset_full_dir, folder)
            with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
                response_status = {}
                for config_folder in FaultyDataFilterer.CONFIG_FOLDERS:
                    log_path = FileUtils.extract_file_path_from_zipped(zip_file, config_folder, 'log.json')
                    if log_path:
                        with zipfile.open(log_path) as log_file:
                            log_data = FileUtils.read_from_json_zipped_file(log_file)
                        response_status_code = log_data["Status"]
                        response_status[config_folder] = response_status_code

                is_any_value_not_200 = any(value != 200 for value in response_status.values())
                if is_any_value_not_200:
                    non_code_200_data[folder] = response_status
                else: 
                    code_200_data[folder] = response_status
        
        output_path_200 = os.path.join('filter', f"{date}_response_code_200_status.json")
        FileUtils.save_as_json_output(output_path_200, code_200_data)
        
        output_path_non_200 = os.path.join('filter', f"{date}_response_non_200_status.json")
        FileUtils.save_as_json_output(output_path_non_200, non_code_200_data)
        
        return len(code_200_data), len(non_code_200_data)

    def get_seperate_list_of_blocked_data(self, json_file):
        data = FileUtils.read_from_json_file(json_file)
        
        both = []
        self_ref = []
        no_ref = []

        for key, value in data.items():
            self_ref_value = value.get('self_ref')
            no_ref_value = value.get('no_ref')

            if self_ref_value != 200 and no_ref_value != 200:
                both.append(key)
            elif self_ref_value != 200:
                self_ref.append(key)
            elif no_ref_value != 200:
                no_ref.append(key)
        
        blocked_lists_dict = {
            "both": both,
            "self_ref": self_ref, 
            "no_ref": no_ref
        }

        return blocked_lists_dict


    def filter_blocked_page_by_category(self, date, parent_path, blocked_dir, cat, blocked_list):
        status = []

        blocked_sub_dir = os.path.join(blocked_dir, cat)
        FileUtils.check_and_create_folder(blocked_sub_dir)
        
        for folder in blocked_list:
            zip_dataset_path = os.path.join(parent_path, folder)
            if (os.path.exists(zip_dataset_path)):
                shutil.move(zip_dataset_path, blocked_sub_dir)
            else:
                status.append(folder)
        
        blocked_page_cat_folder = os.path.join("filter", "blocked_page", "block_page_cat_logs")
        FileUtils.check_and_create_folder(blocked_page_cat_folder)
        output_path = os.path.join(blocked_page_cat_folder, f"{date}_blocked_page_cat_failed.txt")
        FileUtils.export_output_as_txt_file(output_path, status)


    def filter_block_page(self, folder, month, date, phishing_mode):
        if phishing_mode == "phishing":
            parent_path = FileUtils.get_complete_phishing_dataset_parent_path(folder, month, date)
            filter_logs_folder_path = os.path.join(folder, month, f'dataset_{date}', f'dataset_{date}', 'filter_logs')
        else:
            parent_path = FileUtils.get_complete_benign_dataset_parent_path(folder, month)
            filter_logs_folder_path = os.path.join(folder, month, 'filter_logs')
        
        blocked_dataset_txt_file_path = os.path.join(filter_logs_folder_path, f"{date}_response_non_200_status.json")
        blocked_lists_dict = self.get_seperate_list_of_blocked_data(blocked_dataset_txt_file_path)

        dir_to_store_blocked_samples = os.path.join(parent_path, "blocked")
        FileUtils.check_and_create_folder(dir_to_store_blocked_samples)

        blocked_cats = ["both", "self_ref", "no_ref"]
        for cat in blocked_cats:
            self.filter_blocked_page_by_category(date, parent_path, dir_to_store_blocked_samples, cat, blocked_lists_dict.get(cat))
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    parser.add_argument("folder", help="Name of dataset folder path")
    parser.add_argument("folder", help="Month of dataset")
    parser.add_argument("date", help="Date of dataset")
    parser.add_argument("phishing_mode", choices=['phishing', 'benign'], help="phishing or benign")
    args = parser.parse_args()
    
    date_specific_dataset_folder = os.path.join(args.folder, args.month, args.date)

    response_status_filter = ResponseStatusFilterer()
    num_of_complete_200, num_of_complete_non_200 = response_status_filter.consolidate_reponse_status(date_specific_dataset_folder, args.date)
    response_status_filter.filter_block_page(args.folder, args.month, args.date, args.phishing_mode)