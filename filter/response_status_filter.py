
import os
import zipfile

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