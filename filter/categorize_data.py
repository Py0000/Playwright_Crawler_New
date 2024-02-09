import json
import os
import shutil 



def read_faulty_files_as_list(txt_file):
    with open(txt_file, "r") as f: 
        faulty_folder_names = f.readlines()
    
    # Remove newline characters and any whitespace
    faulty_folder_list = [folder_name.strip() for folder_name in faulty_folder_names]

    return faulty_folder_list


def categorize(date, dataset_path, faulty_txt, new_dir):
    status = {}

    faulty_path = os.path.join(dataset_path, new_dir)
    if not os.path.exists(faulty_path):
        os.makedirs(faulty_path)

    both_faulty_folder_names = read_faulty_files_as_list(faulty_txt)
    num_of_faulty = len(both_faulty_folder_names)

    for folder in both_faulty_folder_names:
        zip_folder_path = os.path.join(dataset_path, folder)

        if (os.path.exists(zip_folder_path)):
            shutil.move(zip_folder_path, faulty_path)
        else:
            status[folder] = "Failed"

    output_path = f"{date}_{new_dir}_categorization_failed.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(status, f, ensure_ascii=False, indent=4)
    
    os.remove(faulty_txt)
    return num_of_faulty

def clean_up_complete_data(dataset_path):
    complete_path = os.path.join(dataset_path, "complete_dataset")
    if not os.path.exists(complete_path):
        os.makedirs(complete_path)

    count = 0
    datasets = os.listdir(dataset_path)
    for folder in datasets:
        zip_folder_path = os.path.join(dataset_path, folder)
        if zip_folder_path.endswith(".zip"):
            shutil.move(zip_folder_path, complete_path)
            count += 1
    
    return count





