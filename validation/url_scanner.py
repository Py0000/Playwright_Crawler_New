import requests
import os
import json
import time

import utils

VENDOR_OPENPHISH = "OpenPhish"
VENDOR_GOOGLE_SAFEBROWSING = "Google Safebrowsing"
VENDOR_KASPERSKY = "Kaspersky"
VENDOR_TRUSTWAVE = "Trustwave"
VENDORS_OF_INTEREST = [VENDOR_OPENPHISH, VENDOR_GOOGLE_SAFEBROWSING, VENDOR_KASPERSKY, VENDOR_TRUSTWAVE]


def is_data_ready(report):
    for vendor in VENDORS_OF_INTEREST:
        result = report.get("data", {}).get("attributes", {}).get("results", {}).get(vendor)
        if not result:
            return False
    
    return True


# Folder will be the orginal_dataset_{date} folder used for screenshot comparision as well
def get_url_to_validate(original_dataset_path):
    print("Getting urls for scanning...")
    # Gets the url to be used for validation
    url_to_file_hash_dict = {}

    # Loop through the list of zipped dataset folders
    folders = os.listdir(original_dataset_path)
    for folder in folders:
        # Account for different zipping and unzipping structure
        log_file_path = utils.generate_file_path(original_dataset_path, folder, 'log.json')
        
        # Get the url of the feed as well as the file hash
        with open(log_file_path, 'r') as file:
            data = json.load(file)
        url = data["Provided Url"]
        hash_value = data["Provided Url Hash (in SHA-256)"]

        url_to_file_hash_dict[url] = hash_value
    
    return url_to_file_hash_dict


# Submits url to be scan in VirusTotal
def scan_url(url_to_file_hash_dict, api_key):
    consolidate_data = {}

    # VirusTotal API key (required to use the VirusTotal API)
    headers = {'x-apikey': api_key}

    # Loop through the selected url 
    count = 1
    for url, hash in url_to_file_hash_dict.items():
        print(f"\nScanning Url #{count}...")
        print(f"Url: {url}")
        # Send each url for scanning on VirusTotal
        response = requests.post(
            'https://www.virustotal.com/api/v3/urls', 
            headers=headers, 
            data={'url': url}
        )
        
        if response.status_code == 200:
            # Get the scan report id for this url
            url_id = response.json()['data']['id']

            # Extract the information we are interested in from the scan report
            vendors_flagged_red, vendor_of_interest_status = get_url_analysis_report(url_id, api_key)

            current_data = {
                "File Hash": hash,
                "Website URL": url,
                "# Vendors Flagged Red": vendors_flagged_red,
                "OpenPhish": vendor_of_interest_status[VENDOR_OPENPHISH],
                "Google Safebrowsing": vendor_of_interest_status[VENDOR_GOOGLE_SAFEBROWSING],
                "Kaspersky": vendor_of_interest_status[VENDOR_KASPERSKY],
                "Trustwave": vendor_of_interest_status[VENDOR_KASPERSKY]
            }
            
            consolidate_data[hash] = current_data

        else:
            print(f"URL: {url} - Error: {response.text}")
            consolidate_data[hash] = f"Error: {response.text}"
        
        count = count + 1
        
    return consolidate_data


# Get the scan analysis report
def get_url_analysis_report(url_id, api_key):
    max_attempt = 10
    for attempt in range(max_attempt):
        response = requests.get(
            f'https://www.virustotal.com/api/v3/analyses/{url_id}',
            headers={'x-apikey': api_key}
        )

        report = response.json()
        is_interested_available = is_data_ready(report)

        if is_interested_available:
            # Extracts the relevant data that we are interested in
            return extract_relevant_data_from_analysis_report(report)

        time.sleep((attempt + 1) * 3)


def get_flagged_count(results):
    PHISHING_INDICATOR = ['phishing', 'malware', 'malicious']
    phishing_count = sum(vendor['result'] in PHISHING_INDICATOR for vendor in results.values())
    return phishing_count

def get_vendor_status(results):
    vendor_of_interest_status = {}
    for vendor in VENDORS_OF_INTEREST:
        if vendor in results:
            vendor_result = results[vendor]
            status = vendor_result['result']
            vendor_of_interest_status[vendor] = status.capitalize()
    
    return vendor_of_interest_status


def extract_relevant_data_from_analysis_report(report):
    # Contains the status of each security vendor for the submitted url
    results = report["data"]["attributes"]["results"]
    num_of_vendors = len(results)

    # Get the number of vendors that flagged the url as red
    phishing_count = get_flagged_count(results)

    # Check the status of the 4 vendors we are interested in
    vendor_of_interest_status = get_vendor_status(results)

    vendors_flagged_red = f'="{phishing_count}/{num_of_vendors}"'

    print(vendors_flagged_red)
    print(vendor_of_interest_status)
    return vendors_flagged_red, vendor_of_interest_status



def url_scanner(original_dataset_folder_path, date, api_key):
    url_to_file_hash_dict = get_url_to_validate(original_dataset_folder_path)
    validation_data = scan_url(url_to_file_hash_dict, api_key)
    utils.generate_csv_report(validation_data, f"{date}_url_validation.csv")
    

