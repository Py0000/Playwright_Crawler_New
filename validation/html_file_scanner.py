import os
import requests
import time

import utils

def get_html_files_for_scanning(original_dataset_path):
    html_data = {}

    folders = os.listdir(original_dataset_path)
    for folder in folders:
        try:
            # Account for different zipping and unzipping structure
            html_file_path = utils.generate_file_path(original_dataset_path, folder, 'html_script_aft.html')
            print(f"File exist for {folder}: {os.path.exists(html_file_path)}")
            with open(html_file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            
            files = {
                'file': ('filename.html', html_content)
            }

            html_data[os.path.basename(folder)] = files
        except Exception as e:
            print(f"Error for {folder}: {e}")

    return html_data


def scan_html_file(html_data_list, api_key):
    consolidate_data = {}
    headers = {'x-apikey': api_key}

    count = 1
    for hash, file in html_data_list.items():
        print(f"\nScanning File #{count}...")
        # Send each url for scanning on VirusTotal
        response = requests.post(
            'https://www.virustotal.com/api/v3/files', 
            headers=headers, 
            files=file
        )

        print(response.status_code)
        if response.status_code == 200:
            analysis_id = response.json()['data']['id']
            vendors_flagged_red = get_html_analysis_report(analysis_id, api_key)

            current_data = {
                "File Hash": hash,
                "Direct HTML Script Analysis by VirusTotal": vendors_flagged_red
            }

            consolidate_data[hash] = current_data
        
        else:
            print(f"Error: {response.text}")
        
        count += 1

    return consolidate_data



def get_html_analysis_report(analysis_id, api_key):
    max_attempt = 10
    for attempt in range(max_attempt):
        response = requests.get(
            f'https://www.virustotal.com/api/v3/analyses/{analysis_id}',
            headers={'x-apikey': api_key}
        )

        report = response.json()
        is_ready = report.get('data', {}).get('attributes', {}).get('status', 'unknown') == 'completed'
        if is_ready:
            return extract_total_value(report)
        else:
            time.sleep((attempt + 2) * 3)

def get_flagged_count(results):
    return sum(1 for vendor in results.values() if vendor['result'] is not None)

def extract_total_value(report):
    # Contains the status of each security vendor for the submitted url
    results = report["data"]["attributes"]["results"]
    num_of_vendors = len(results)

    # Get number of vendors flagging the html file as red
    flagged_count = get_flagged_count(results)
    
    vendors_flagged_red = f'="{flagged_count}/{num_of_vendors}"'
    print(vendors_flagged_red)
    return vendors_flagged_red



def html_file_scanner(original_dataset_folder_path, date, api_key):
    html_data_list = get_html_files_for_scanning(original_dataset_folder_path)
    validation_data = scan_html_file(html_data_list, api_key)
    utils.generate_csv_report(validation_data, f"{date}_html_verification.csv")
    