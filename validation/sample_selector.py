import argparse
import json
import os
from shutil import copy2
import shutil
import zipfile
from utils.file_utils import FileUtils

class SampleSelector:
    def __init__(self, verified_txt, exclude_txt, max_limit):
        self.already_verified = self.setup_selector(verified_txt)
        self.to_exclude = self.setup_selector(exclude_txt)
        self.max_limit = max_limit

    def setup_selector(self, txt_file):
        result = []
        try:
            with open(txt_file, 'r') as file:
                for line in file:
                    result.append(line.strip())
        except:
            pass
        return result
    
    def select_samples(self, dataset_dir, month, date, phishing_mode):
        target_path_folder = os.path.join("validation", "new_samples", f"dateset_{date}")
        FileUtils.check_and_create_folder(target_path_folder)
        
        if phishing_mode == "phishing":
            folder_path = FileUtils.get_complete_phishing_dataset_parent_path(dataset_dir, month, date)
        else:
            folder_path = FileUtils.get_complete_benign_dataset_parent_path(dataset_dir, month, date)
        
        copied_count = 0
        added_hash = []
        length = len(os.listdir(folder_path))
        for folder in os.listdir(folder_path):
            if copied_count >= self.max_limit:
                break

            if not folder.endswith(".zip"):
                continue
                
            folder_hash = folder.replace(".zip", "")
            if folder_hash not in self.already_verified:
                file_path = os.path.join(folder_path, folder)
                copy2(file_path, target_path_folder)
                copied_count += 1
                added_hash.append(folder_hash)
        
            if copied_count % 100 == 0 and copied_count != 0:
                print(f"Count: {copied_count} | {(copied_count/length)*100}% complete...")

        return target_path_folder

    def copy_screenshot_out(self, target_path_folder, date):
        target_path_ss = os.path.join("validation", "screenshots", f"dateset_{date}")
        FileUtils.check_and_create_folder(target_path_ss)
        data = []
        for folder in os.listdir(target_path_folder):
            hash_value = folder.replace(".zip", "")
            if hash_value not in self.to_exclude:
                with zipfile.ZipFile(os.path.join(target_path_folder, folder), 'r') as zip_ref:
                    log_path = FileUtils.extract_file_path_from_zipped(zip_ref, 'self_ref', 'log.json')
                    if log_path:
                        with zip_ref.open(log_path) as log_file:
                            log_data = json.load(log_file)
                            url = log_data["Url visited"]
                            data.append({'Hash': hash_value, 'URL': url})

                    screenshot_path = FileUtils.extract_file_path_from_zipped(zip_ref, 'self_ref', 'screenshot_aft.png')
                    if screenshot_path:
                        zip_ref.extract(screenshot_path, target_path_ss)
                        original_screenshot_path = os.path.join(target_path_ss, screenshot_path)
                        new_screenshot_path = os.path.join(target_path_ss, f"{hash_value}.png")
                        shutil.copy(original_screenshot_path, new_screenshot_path)
                        os.remove(original_screenshot_path)
                        os.removedirs(os.path.dirname(original_screenshot_path))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Select samples")
    parser.add_argument("dataset_dir", help="Name of the dataset folder path")
    parser.add_argument("month", help="Month of dataset")
    parser.add_argument("date", help="Date of dataset")
    parser.add_argument("phishing_mode", choices=["phishing", "benign"], help="Phishing or Benign")
    parser.add_argument("verified", help="file path to verified samples txt")
    parser.add_argument("exclude", help="file path to samples to exclude txt")
    parser.add_argument("limit", help="Number of samples to select")
    args = parser.parse_args()

    sample_selector = SampleSelector(args.verified, args.exclude, args.limit)
    target_path_folder = sample_selector.select_samples(args.dataset_dir, args.month, args.date, args.phishing_mode)
    sample_selector.copy_screenshot_out(target_path_folder, args.date)

    

        



        
