

import os
from shutil import copy2
import zipfile
import json

already_verified = []
with open('verified.txt', 'r') as file:
    for line in file:
        already_verified.append(line.strip())

to_exclude = []
with open('exclude.txt', 'r') as file:
    for line in file:
        to_exclude.append(line.strip())
        already_verified.append(line.strip())

month = "Dec"
date = "011223"
dataset_folder_path = os.path.join("datasets", month, f"dataset_{date}", f"dataset_{date}", f"dataset_{date}", "complete_dataset")

target_path = os.path.join("dataset_new_validation", f"dataset_{date}")
if not os.path.exists(target_path):
    os.makedirs(target_path)

copied_count = 0

added_hash = []
for folder in os.listdir(dataset_folder_path):
    if copied_count == 20:
        break

    if not folder.endswith(".zip"):
        continue

    folder_hash = folder.replace(".zip", "")

    if folder_hash not in already_verified:
        file_path = os.path.join(dataset_folder_path, folder)
        copy2(file_path, target_path)
        copied_count += 1
        added_hash.append(folder_hash)
    

for folder in os.listdir(target_path):
    if folder.replace(".zip", "") not in to_exclude:
        print(folder.replace(".zip", ""))

        with zipfile.ZipFile(os.path.join(target_path, folder), 'r') as zip_ref:
            logs_relative_path = os.path.join('self_ref', 'log.json')
            log_file_path = next((zipinfo.filename for zipinfo in zip_ref.infolist() if logs_relative_path in zipinfo.filename), None)
            with zip_ref.open(log_file_path) as log_file:
                log_data = json.load(log_file)
                url = log_data["Url visited"]
        print(url)


    


