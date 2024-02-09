import argparse
import os
import zipfile

import url_scanner
import html_file_scanner
import utils


# Unzip the 10-30 dataset crawled (to be used for validation using VirusTotal)
def unzip_folder(zip_folder_path):
    if not (os.path.isfile(zip_folder_path) and zip_folder_path.endswith('.zip')):
        print("The provided path does not point to a zip file.")
    
    # Extracts the files to the same directory as the zip file
    extracted_folder_path = os.path.splitext(zip_folder_path)[0]
    with zipfile.ZipFile(zip_folder_path, 'r') as zip_ref:
        zip_ref.extractall(extracted_folder_path)

    os.remove(zip_folder_path)
    return extracted_folder_path


def unzip_original_dataset_folder(original_dataset_path):
    print("Unzipping folders...")
    folders = os.listdir(original_dataset_path)
    for folder in folders:
        zipped_original_folder_path = os.path.join(original_dataset_path, folder)
        unzip_folder(zipped_original_folder_path)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    parser.add_argument("original_dataset_folder_path", help="Name of the original dataset folder path")
    parser.add_argument("date", help="Date of dataset")
    args = parser.parse_args()

    api_key_file = 'virus_total_api_key.txt'
    api_key = utils.read_virus_total_api_key(api_key_file)

    unzip_original_dataset_folder(args.original_dataset_folder_path)
    url_scanner.url_scanner(args.original_dataset_folder_path, args.date, api_key)
    html_file_scanner.html_file_scanner(args.original_dataset_folder_path, args.date, api_key)


