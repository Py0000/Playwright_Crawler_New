import json
import os
import re
import zipfile
import shutil

def get_common_pattern():
    # Detects the use of eval()
    eval_pattern = re.compile(r'\beval\s*\(')  
    window_document_pattern = re.compile(r'(window|document)\[\s*[\'"][^\'"]+[\'"]\s*\]')

    # Other potentials 
    """
    long_string = re.compile(r'(["\']).{40,}\1')  # Detects strings longer than 40 characters
    hex_encoding = re.compile(r'\\x[0-9a-fA-F]{2}')  # Detects hexadecimal character encoding
    """

    return [eval_pattern, window_document_pattern]


def is_obfuscated(html_script):
    common_obfuscation_pattern = get_common_pattern()

    for pattern in common_obfuscation_pattern:
        if pattern.search(html_script):
            return True
    
    return False


def check_html_for_obfuscation(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        return is_obfuscated(content)


def check_dataset(main_directory):
    consolidated_results = {}

    extraction_path = main_directory.replace('.zip', '')
    date = extraction_path.split('_')[-1]
    
    with zipfile.ZipFile(main_directory, 'r') as zip_ref:
        print("\nExtracting zip folder ...")
        zip_ref.extractall(extraction_path)

    parent_folder_path = os.path.join(extraction_path, f'dataset_{date}', f'dataset_{date}', 'complete_dataset')    
    for dir in os.listdir(parent_folder_path):
        current_dataset = dir.replace('.zip', '')
        current_dataset_dir = os.path.join(parent_folder_path, dir)

        with zipfile.ZipFile(current_dataset_dir, 'r') as zip_ref:
            zip_extraction_path = current_dataset_dir.replace('.zip', '')
            print(f"Extracting inner zip folder {dir}...")
            zip_ref.extractall(zip_extraction_path)
            current_dataset_dir = os.path.join(zip_extraction_path, current_dataset)
        
        dataset_status = {}
        for sub_dir in os.listdir(current_dataset_dir):
            current_dataset_ref_dir = os.path.join(current_dataset_dir, sub_dir)
            current_dataset_html_file_aft = os.path.join(current_dataset_ref_dir, 'html_script_aft.html')
            current_dataset_html_file_bef = os.path.join(current_dataset_ref_dir, 'html_script_bef.html')

            is_aft_potentially_obfuscated = check_html_for_obfuscation(current_dataset_html_file_aft)
            is_bef_potentially_obfuscated = check_html_for_obfuscation(current_dataset_html_file_bef)

            status = {
                "Html Script (Before)": "Potentially Obfuscated" if is_bef_potentially_obfuscated else "Not obfuscated",
                "Html Script (After)": "Potentially Obfuscated" if is_aft_potentially_obfuscated else "Not obfuscated",
            }

            dataset_status[sub_dir] = status
        
        consolidated_results[current_dataset] = dataset_status
    
    base_output_dir = f"primary_logs/{date}"
    if not os.path.exists(base_output_dir):
        os.makedirs(base_output_dir)
    
    consolidated_output = os.path.join(base_output_dir, f"{date}_consolidation.json")
    with open(consolidated_output, 'w', encoding='utf-8') as f:
        json.dump(consolidated_results, f, ensure_ascii=False, indent=4)
    

    shutil.rmtree(extraction_path)