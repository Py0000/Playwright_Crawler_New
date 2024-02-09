import json
import os 
import zipfile



CONFIG_FOLDERS = ["self_ref", "no_ref"]
LOG_FILE_NAME = "log.json"
LOG_FIELDS_TO_SKIP = ["Url visited", "Provided Url", "Has Url changed", "Provided Url Hash (in SHA-256)", "Time crawled", "Time taken", "Mouse moved when obtaining server-side data?"]

def get_log_file_data(log_file_path, zip_file):
    if log_file_path in zip_file.namelist():
        with zip_file.open(log_file_path) as log_file:
            log_data = json.load(log_file)
        return log_data
    
    return None

def export_data_as_txt_file(filename, data):
    with open(filename, 'w') as f:
        for item in data:
            f.write(str(item) + '\n')

def export_data(date, dual_faulty_data, self_ref_faulty_only_data, no_ref_faulty_only_data):
    export_data_as_txt_file(f"{date}_dual_faulty_dataset.txt", dual_faulty_data)
    export_data_as_txt_file(f"{date}_self_ref_only_faulty_dataset.txt", self_ref_faulty_only_data)
    export_data_as_txt_file(f"{date}_no_ref_only_faulty_dataset.txt", no_ref_faulty_only_data)


def obtain_real_file_path(zip_file, zip_file_path, current_folder):
    # Obtain the folder hash for this particular dataset 
    folder_hash = os.path.splitext(os.path.basename(current_folder))[0]

    """
    # Check if the zip folder contains this additional folder
    potential_file_path = os.path.join(zip_file_path, folder_hash)
    if potential_file_path in zip_file.namelist():
        file_path = potential_file_path
    else:
        file_path = zip_file_path
    """
    return folder_hash


def check_status_for_ref_config(zip_file, file_path):
    folder_status = {}
    # response_status = {}
    for config_folder in CONFIG_FOLDERS:
        log_file_path = os.path.join(file_path, config_folder, LOG_FILE_NAME)
        log_data = get_log_file_data(log_file_path, zip_file)
        if log_data != None:
            has_error = any("Error" in value for key, value in log_data.items() if isinstance(value, str) and key not in LOG_FIELDS_TO_SKIP)

            if has_error:
                folder_status[config_folder] = "Faulty"
            else:
                folder_status[config_folder] = "Complete"
            
            # Can get the status from log.json also 
            # TODO: Fill in logic 
            # response_status_code = log_data["Status"]
            #if (response_status_code != 200):
                

    return folder_status

    
def filter_faulty_dataset(dataset_directory, date):
    dual_faulty_data = []
    self_ref_faulty_only_data = []
    no_ref_faulty_only_data = []

    datasets = os.listdir(dataset_directory)
    total_count = 0
    for folder in datasets:
        print(f"\nProcessing {folder}...")
        if folder.endswith(".zip"):
            total_count += 1
            zip_file_path = os.path.join(dataset_directory, folder)
            with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
                # Checks if there are any additional folders contained between zip folder and ref_config folders due to zipping difference
                file_path = obtain_real_file_path(zip_file, zip_file_path, folder)
                
                # Get the log file, check if there is any error in any of the data collection stage for each ref_config
                folder_status = check_status_for_ref_config(zip_file, file_path)
                print("Folder status: ", folder_status)
                
                if all(value == "Faulty" for value in folder_status.values()):
                    dual_faulty_data.append(folder)
                
                elif folder_status["self_ref"] == "Faulty":
                    self_ref_faulty_only_data.append(folder)
                
                elif folder_status["no_ref"] == "Faulty":
                    no_ref_faulty_only_data.append(folder)
                

        print(f"Done Processing {folder}...")


    export_data(date, dual_faulty_data, self_ref_faulty_only_data, no_ref_faulty_only_data)
    return total_count



