import json
import os
from urllib.parse import urlparse

import util_def


# Generates a semaphore lock file to signal that data for the folder is complete and ready to be sent to database.
def generate_semaphore_lock_file(folder_path):
    semaphore_file_path = os.path.join(folder_path, util_def.SEMAPHORE_FILE)
    with open(semaphore_file_path, 'w') as flag_file:
        flag_file.write('')


# Saves the data obtained into a json file at the outpath path
def save_data_to_json_format(outpath_path, data):
    with open(outpath_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# Returns the base folder name used to stored crawled data
# Either dataset/self_ref or dataset/no_ref
def get_crawled_dataset_base_folder_name(ref_flag):
    base_folder_name = util_def.REF_SET if ref_flag else util_def.NO_REF_SET
    return base_folder_name


# Generates the base folder (i.e dataset/self_ref or dataset/no_ref) which is used to store the crawled data
def generate_base_folder_for_crawled_dataset(url_hash_folder_name, dataset_folder_name, ref_flag):
    ref_folder_name = get_crawled_dataset_base_folder_name(ref_flag)
    base_folder_path = os.path.join(dataset_folder_name, url_hash_folder_name, ref_folder_name)

    if not os.path.exists(base_folder_path):
        os.makedirs(base_folder_path)
    
    return base_folder_path


# Generates the individual folder for each url (i.e. dataset/self_ref/hash, etc)
def generate_network_folders(base_folder_path):
    network_folders = [util_def.FOLDER_NETWORK_REQUEST_FRAGMENTS, util_def.FOLDER_NETWORK_RESPONSE_FRAGMENTS]
    for folder in network_folders:
        path = os.path.join(base_folder_path, folder)
        if not os.path.exists(path):
            os.makedirs(path)



# Extracts the hostname of an url
def extract_hostname(website_url):
    parsed_url = urlparse(website_url)
    hostname = parsed_url.hostname
    return hostname



def get_analysis_folder_path(dataset_folder_path):
    # Splitting path into components
    parts = os.path.normpath(dataset_folder_path).split(os.sep)

    # Extracting the last two components
    sub_folder_path = os.path.join(parts[-2], parts[-1])

    output_path = os.path.join(util_def.FOLDER_ANALYSIS_BASE, sub_folder_path)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    return output_path