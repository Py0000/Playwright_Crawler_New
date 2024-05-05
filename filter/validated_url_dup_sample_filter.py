import os
import shutil
from utils.file_utils import FileUtils

original_validated_folder = os.path.join('datasets', 'validated')
target_folder = os.path.join('datasets', 'validated_dup')

hash_dict = {}
dup_data = FileUtils.read_from_json_file(os.path.join('filter', 'url_portion_check', 'dup_only_analysis.json'))
for key, lists in dup_data.items():
    for item in lists[1:]:  # Skip the first item of each list
        date = item[0]
        hash_value = item[1]

        if date in hash_dict:
            hash_dict[date].append(hash_value)
        else:
            hash_dict[date] = [hash_value]




if not os.path.exists(target_folder):
    os.makedirs(target_folder)

for date, hashes in hash_dict.items():
    current_folder = os.path.join(original_validated_folder, f'original_dataset_{date}')
    if os.path.exists(current_folder):
        for hash_value in hashes:
            zip_file_path = os.path.join(current_folder, f"{hash_value}.zip")
            if os.path.exists(zip_file_path):
                target_path = os.path.join(target_folder, f"{hash_value}.zip")
                shutil.move(zip_file_path, target_path)
                print(f'Moved {zip_file_path} to {target_path}')
            else:
                print(f'File not found: {zip_file_path}')
    else:
        print(f'Folder not found: {current_folder}')
      
