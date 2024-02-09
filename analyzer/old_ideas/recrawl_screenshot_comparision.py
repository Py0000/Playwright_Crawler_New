from PIL import Image
import imagehash
import json
import os
import zipfile
import argparse

import generate_screenshot_comparison_csv as gscc

def compute_phash(image_path):
    try:
        with Image.open(image_path) as img:
            hash_val = imagehash.phash(img)
        return hash_val
    except Exception as e:
        return f"Error computing pHash: {e}"


def compute_dhash(image_path):
    try:
        with Image.open(image_path) as img:
            hash_val = imagehash.dhash(img)
        return hash_val
    except Exception as e:
        return f"Error computing dHash: {e}"
    

def compute_hashes(image_path):
    pHash = compute_phash(image_path)
    dHash = compute_dhash(image_path)
    
    return pHash, dHash

def compute_hash_difference(hash1, hash2):
    if isinstance(hash1, str):
        return hash1

    if isinstance(hash2, str):
        return hash2
    
    return abs(hash1 - hash2)


def unzip_folder(zip_folder_path):
    if not (os.path.isfile(zip_folder_path) and zip_folder_path.endswith('.zip')):
        print("The provided path does not point to a zip file.")
    
    # Extracts the files to the same directory as the zip file
    extracted_folder_path = os.path.splitext(zip_folder_path)[0]
    with zipfile.ZipFile(zip_folder_path, 'r') as zip_ref:
        zip_ref.extractall(extracted_folder_path)
    
    print("Extracted to: ", extracted_folder_path)
    return extracted_folder_path




# original_dataset_path: Original 10-30 dataset folder (non-zipped)
def get_hashes_of_original_dataset(original_dataset_path):
    consolidated_data = {}
    # Loop through all files in this folder to unzip them 
    folders = os.listdir(original_dataset_path)
    for folder in folders:
        zipped_original_folder_path = os.path.join(original_dataset_path, folder)
        unzipped_folder_name = unzip_folder(zipped_original_folder_path)

        # Get the screenshot_aft for no_ref and self_ref
        self_ref_screenshot_path = os.path.join(unzipped_folder_name, os.path.basename(unzipped_folder_name), 'self_ref', 'screenshot_aft.png')
        no_ref_screenshot_path = os.path.join(unzipped_folder_name, os.path.basename(unzipped_folder_name), 'no_ref', 'screenshot_aft.png')

        # Compute the hash value
        if not os.path.exists(self_ref_screenshot_path):
            self_ref_screenshot_path = os.path.join(unzipped_folder_name, 'self_ref', 'screenshot_aft.png')
        if not os.path.exists(no_ref_screenshot_path):
            no_ref_screenshot_path = os.path.join(unzipped_folder_name, 'no_ref', 'screenshot_aft.png')

        self_ref_phash, self_ref_dhash = compute_hashes(self_ref_screenshot_path)    
        no_ref_phash, no_ref_dhash = compute_hashes(no_ref_screenshot_path)

        # Save the results of the hash value (for later use)
        current_dataset_hashes = {
            os.path.basename(unzipped_folder_name): {
                "self_ref_phash": self_ref_phash,
                "self_ref_dhash": self_ref_dhash,
                "no_ref_phash": no_ref_phash,
                "no_ref_dhash": no_ref_dhash
            }
        }

        consolidated_data.update(current_dataset_hashes)
    
    return consolidated_data
        


def get_hashes_of_recrawled_dataset(recrawled_dataset_path):
    consolidated_data = {}

    # Unzip the main recrawled_dataset folder first
    unzipped_folder_name = unzip_folder(recrawled_dataset_path)
    dataset_folder = os.path.join(unzipped_folder_name, os.path.basename(unzipped_folder_name))

    # Loop through all files in this folder 
    folders = os.listdir(dataset_folder)
    for folder in folders:
        current_folder_path = os.path.join(dataset_folder, folder)

        # Get the screenshot_aft for no_ref and self_ref
        self_ref_screenshot_path = os.path.join(current_folder_path, 'self_ref', 'screenshot_aft.png')
        no_ref_screenshot_path = os.path.join(current_folder_path, 'no_ref', 'screenshot_aft.png')

        # Compute the hash value
        self_ref_phash, self_ref_dhash = compute_hashes(self_ref_screenshot_path)
        no_ref_phash, no_ref_dhash = compute_hashes(no_ref_screenshot_path)

        # Save the results of the hash value (for later use)
        current_dataset_hashes = {
            folder: {
                "self_ref_phash": self_ref_phash,
                "self_ref_dhash": self_ref_dhash,
                "no_ref_phash": no_ref_phash,
                "no_ref_dhash": no_ref_dhash
            }
        }

        consolidated_data.update(current_dataset_hashes)

    return consolidated_data


def generate_hash_difference_report(original_dataset_path, recrawled_dataset_path, date):
    original_dataset_hashes_dict = get_hashes_of_original_dataset(original_dataset_path)
    recrawled_dataset_hashes_dict = get_hashes_of_recrawled_dataset(recrawled_dataset_path)
    print(f"Length of original dataset hashes: {len(original_dataset_hashes_dict)}")
    print(f"Length of recrawled dataset hashes: {len(recrawled_dataset_hashes_dict)}")

    hash_differences = {}
    for folder_name in original_dataset_hashes_dict:
        print(f"Folder_name: {folder_name} matched? {folder_name in recrawled_dataset_hashes_dict}")
        if folder_name in recrawled_dataset_hashes_dict:
            original = original_dataset_hashes_dict[folder_name]
            recrawled = recrawled_dataset_hashes_dict[folder_name]

            self_ref_phash_diff = compute_hash_difference(original['self_ref_phash'], recrawled['self_ref_phash'])
            self_ref_dhash_diff = compute_hash_difference(original['self_ref_dhash'], recrawled['self_ref_dhash'])
            no_ref_phash_diff = compute_hash_difference(original['no_ref_phash'], recrawled['no_ref_phash'])
            no_ref_dhash_diff = compute_hash_difference(original['no_ref_dhash'], recrawled['no_ref_dhash'])

            hash_differences[folder_name] = {
                "self_ref_phash_diff": self_ref_phash_diff,
                "self_ref_dhash_diff": self_ref_dhash_diff,
                "no_ref_phash_diff": no_ref_phash_diff,
                "no_ref_dhash_diff": no_ref_dhash_diff
            }
    
    print(f"Length of consolidated hash_differences: {len(hash_differences)}")
    output_file_name = f"{date}_screenshot_hashes.json"
    with open(output_file_name, 'w', encoding='utf-8') as file:
        json.dump(hash_differences, file, ensure_ascii=False, indent=4)
    
    return output_file_name



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    parser.add_argument("original_dataset_folder_path", help="Name of the original dataset folder path")
    parser.add_argument("recrawled_dataset_folder_path", help="Name of the recrawled dataset folder path")
    parser.add_argument("date", help="Date of dataset")
    parser.add_argument("file_hash_order", help="Name of the txt file that contains the file hash order")
    args = parser.parse_args()

    json_report = generate_hash_difference_report(args.original_dataset_folder_path, args.recrawled_dataset_folder_path, args.date)
    
    if os.path.exists(json_report):
        gscc.generate_csv_for_screenshot(json_report, args.file_hash_order, args.date)
        #os.remove(json_report)
    else:
        print("JSON report not generated...")



