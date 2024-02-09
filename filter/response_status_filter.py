import json
import os 
import zipfile

import faulty_data_filter

def consolidate_reponse_status(dataset_directory, date):
    code_200_data = {}
    non_code_200_data = {}
    complete_dataset_full_dir = os.path.join(dataset_directory, "complete_dataset")
    complete_datasets = os.listdir(complete_dataset_full_dir)
    for folder in complete_datasets:
        if folder.endswith(".zip"):
            zip_file_path = os.path.join(complete_dataset_full_dir, folder)
            with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
                file_path = faulty_data_filter.obtain_real_file_path(zip_file, zip_file_path, folder)

                response_status = {}
                for config_folder in faulty_data_filter.CONFIG_FOLDERS:
                    log_file_path = os.path.join(file_path, config_folder, faulty_data_filter.LOG_FILE_NAME)
                    log_data = faulty_data_filter.get_log_file_data(log_file_path, zip_file)
                    if log_data != None:
                        response_status_code = log_data["Status"]
                        response_status[config_folder] = response_status_code

                is_any_value_not_200 = any(value != 200 for value in response_status.values())
                if is_any_value_not_200:
                    non_code_200_data[folder] = response_status
                else: 
                    code_200_data[folder] = response_status
    
    output_path_200 = f"{date}_response_code_200_status.json"
    with open(output_path_200, 'w', encoding='utf-8') as f:
        json.dump(code_200_data, f, ensure_ascii=False, indent=4)
    
    output_path_non_200 = f"{date}_response_non_200_status.json"
    with open(output_path_non_200, 'w', encoding='utf-8') as f:
        json.dump(non_code_200_data, f, ensure_ascii=False, indent=4)
    
    return len(code_200_data), len(non_code_200_data)


