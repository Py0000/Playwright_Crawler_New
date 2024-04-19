
import os
import shutil
import zipfile

from tqdm import tqdm
from utils.file_utils import FileUtils

class FaultyDataFilterer:
    LOG_FIELDS_TO_SKIP = ["Url visited", "Provided Url", "Has Url changed", "Provided Url Hash (in SHA-256)", "Time crawled", "Time taken", "Mouse moved when obtaining server-side data?"]
    CONFIG_FOLDERS = ["self_ref", "no_ref"]

    def __init__(self):
        pass

    def check_status_for_ref_config(self, zip_ref):
        folder_status = {}
        for config_folder in self.CONFIG_FOLDERS:
            log_path = FileUtils.extract_file_path_from_zipped(zip_ref, config_folder, 'log.json')
            if log_path:
                with zipfile.open(log_path) as log_file:
                    log_data = FileUtils.read_from_json_zipped_file(log_file)
                
                has_error = any("Error" in value for key, value in log_data.items() if isinstance(value, str) and key not in self.LOG_FIELDS_TO_SKIP)
                if has_error:
                    folder_status[config_folder] = "Faulty"
                else:
                    folder_status[config_folder] = "Complete"
                
            else:
                folder_status[config_folder] = "Faulty"
    

    def filter_faulty_dataset(self, date_specific_dataset_folder, date):
        dual_faulty_data = []
        self_ref_faulty_only_data = []
        no_ref_faulty_only_data = []

        total_count = 0
        for folder in tqdm(os.listdir(date_specific_dataset_folder)):
            if not folder.endswith(".zip"):
                continue

            zip_file_path = os.path.join(date_specific_dataset_folder, folder)
            with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
                folder_status = self.check_status_for_ref_config(zip_file)

                if all(value == "Faulty" for value in folder_status.values()):
                    dual_faulty_data.append(folder)
                elif folder_status["self_ref"] == "Faulty":
                    self_ref_faulty_only_data.append(folder)
                elif folder_status["no_ref"] == "Faulty":
                    no_ref_faulty_only_data.append(folder)
                total_count += 1
        
        self.export_data(date, dual_faulty_data, self_ref_faulty_only_data, no_ref_faulty_only_data)
        return total_count

    def export_data(self, date, dual_faulty_data, self_ref_faulty_only_data, no_ref_faulty_only_data):
        FileUtils.save_as_txt_output(os.path.join('filter', f"{date}_dual_faulty_dataset.txt"), dual_faulty_data)
        FileUtils.save_as_txt_output(os.path.join('filter', f"{date}_self_ref_only_faulty_dataset.txt"), self_ref_faulty_only_data)
        FileUtils.save_as_txt_output(os.path.join('filter', f"{date}_no_ref_only_faulty_dataset.txt"), no_ref_faulty_only_data)

    def read_faulty_files_as_list(self, txt_file):
        with open(txt_file, "r") as f: 
            faulty_folder_names = f.readlines()
        
        # Remove newline characters and any whitespace
        faulty_folder_list = [folder_name.strip() for folder_name in faulty_folder_names]

        return faulty_folder_list

    def categorize_faulty_data(self, date, date_specific_folder, faulty_info_txt, sub_folder_name_to_store):
        status = {}
        sub_path = os.path.join(date_specific_folder, sub_folder_name_to_store)
        FileUtils.check_and_create_folder(sub_path)

        faulty_folder_list = self.read_faulty_files_as_list(faulty_info_txt)
        num_of_faulty = len(faulty_folder_list)
        for folder in faulty_folder_list:
            zip_folder_path = os.path.join(date_specific_folder, folder)
            if (os.path.exists(zip_folder_path)):
                shutil.move(zip_folder_path, sub_path)
            else:
                status[folder] = "Failed"
        
        if len(status) <= 0: 
            output_path = os.path.join('filter', f"{date}_{sub_folder_name_to_store}_categorization_failed.json")
            FileUtils.save_as_json_output(output_path, status)
        
        os.remove(faulty_info_txt)
        return num_of_faulty
    
    def clean_up_complete_data(self, date_specific_folder):
        complete_path = os.path.join(date_specific_folder, "complete_dataset")
        FileUtils.check_and_create_folder(complete_path)

        count = 0
        for folder in os.listdir(date_specific_folder):
            zip_folder_path = os.path.join(date_specific_folder, folder)
            if not zip_folder_path.endswith(".zip"):
                continue
            shutil.move(zip_folder_path, complete_path)
            count += 1
        return count

