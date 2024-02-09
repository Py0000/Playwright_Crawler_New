import json
import os
import shutil

FILE_NETWORK_HAR = "network.har"
FOLDER_NETWORK_FRAGMENTS = "network_data"
FOLDER_NETWORK_RESPONSE_FRAGMENTS = "network_response_files"
FOLDER_NETWORK_REQUEST_FRAGMENTS = "network_request_files"



# Checks if har log file exists in the initial folder 
# If else, obtain all the request and response details from it and return
def obtain_file_details_from_har_log(har_file_path):
    response_file_to_entry_map = None 
    request_file_to_entry_map = None

    if os.path.exists(har_file_path):
        with open(har_file_path, 'r') as f:
            har_data = json.load(f)
            response_file_to_entry_map = {entry['response']['content'].get('_file'): entry for entry in har_data['log']['entries'] if '_file' in entry['response']['content']}
            request_file_to_entry_map = {entry['request']['content'].get('_file'): entry for entry in har_data['log']['entries'] if '_file' in entry['request'].get('content', {})}
        f.close()

    return response_file_to_entry_map, request_file_to_entry_map


def cleanup_initial_data_folder(initial_network_data_path, har_file_path, main_url_folder):
    # Move the har log path out of initial_network_data folder           
    shutil.move(har_file_path, main_url_folder)

    # Delete the initial_network_data folder
    shutil.rmtree(initial_network_data_path)


def move_file(response_data_path, request_data_path, response_file_to_entry_map, ind_data_file_path, ind_data_filename):
    # Check if it is a response datafile
    # If it is move the file to the network_response_data_folder
    response_matched_entry = response_file_to_entry_map.get(ind_data_filename)
    if response_matched_entry:
        shutil.move(ind_data_file_path, os.path.join(response_data_path, ind_data_filename))
    
    # Otherwise, it is network request related datafile, move it to network_request_data_folder
    else:
        shutil.move(ind_data_file_path, os.path.join(request_data_path, ind_data_filename))


def process_network_data_by_ref(url_dataset_folder_path, ref_flag):
    print("\nProcessing network data")
    ref_folder = "self_ref" if ref_flag else "no_ref"
    ref_folder_path = os.path.join(url_dataset_folder_path, ref_folder)
    # Get the path of the folder that contains all the network data initially. This folder is to be removed after processing the network data.
    network_data_path = os.path.join(ref_folder_path, FOLDER_NETWORK_FRAGMENTS)
    
    # Generate the paths to restore the request data and response data respectively after processing
    response_data_path = os.path.join(ref_folder_path, FOLDER_NETWORK_RESPONSE_FRAGMENTS)
    request_data_path = os.path.join(ref_folder_path, FOLDER_NETWORK_REQUEST_FRAGMENTS)

    # Checks that the initial folder (i.e. initial_network_data) exists
    if os.path.exists(network_data_path):
        # Get the har log file path
        har_file_path = os.path.join(network_data_path, FILE_NETWORK_HAR)
        response_file_to_entry_map, request_file_to_entry_map = obtain_file_details_from_har_log(har_file_path)

        # Loop through each file in initial_network_data folder
        for ind_data_filename in os.listdir(network_data_path):
            # Get the filepath for each datafile in the folder    
            ind_data_file_path = os.path.join(network_data_path, ind_data_filename)

            # Skip processing the har log file
            if ind_data_file_path == har_file_path:
                continue
            
            move_file(response_data_path, request_data_path, response_file_to_entry_map, ind_data_file_path, ind_data_filename)
            

        cleanup_initial_data_folder(network_data_path, har_file_path, ref_folder_path)

    print("Done processing network data")



def process_network_data(url_dataset_folder_path):
    process_network_data_by_ref(url_dataset_folder_path, ref_flag=True)
    process_network_data_by_ref(url_dataset_folder_path, ref_flag=False)