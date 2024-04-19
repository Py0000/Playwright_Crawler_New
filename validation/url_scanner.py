
import time
import requests
from tqdm import tqdm

from validation.utils import ValidationUtils

class UrlScanner:
    VENDOR_OPENPHISH = "OpenPhish"
    VENDOR_GOOGLE_SAFEBROWSING = "Google Safebrowsing"
    VENDOR_KASPERSKY = "Kaspersky"
    VENDOR_TRUSTWAVE = "Trustwave"
    VENDORS_OF_INTEREST = [VENDOR_OPENPHISH, VENDOR_GOOGLE_SAFEBROWSING, VENDOR_KASPERSKY, VENDOR_TRUSTWAVE]

    def __init__(self):
        pass

    def generate_data_from_report(self, vendors_flagged_red, vendor_of_interest_status,):
        current_data = {
            "# Vendors Flagged Red": vendors_flagged_red,
            "OpenPhish": vendor_of_interest_status[self.VENDOR_OPENPHISH],
            "Google Safebrowsing": vendor_of_interest_status[self.VENDOR_GOOGLE_SAFEBROWSING],
            "Kaspersky": vendor_of_interest_status[self.VENDOR_KASPERSKY],
            "Trustwave": vendor_of_interest_status[self.VENDOR_TRUSTWAVE]
        }

        return current_data

    def scan_url(self, url_to_file_hash_dict, api_key):
        consolidate_data = {}

        # VirusTotal API key (required to use the VirusTotal API)
        headers = {'x-apikey': api_key}

        for url, hash in tqdm(url_to_file_hash_dict.items()):
            # Send each url for scanning on VirusTotal
            response = requests.post(
                'https://www.virustotal.com/api/v3/urls', 
                headers=headers, 
                data={'url': url}
            )

            if response.status_code == 200:
                url_id = response.json()['data']['id'] # Get the scan report id for this url

                # Extract the information we are interested in from the scan report
                vendors_flagged_red, vendor_of_interest_status = self.get_url_analysis_report(url_id, api_key) 
                current_data = {
                    "File Hash": hash,
                    "Website URL": url,
                    **self.generate_data_from_report(vendors_flagged_red, vendor_of_interest_status)
                }
                consolidate_data[hash] = current_data
            else:
                consolidate_data[hash] = f"Error: {response.text}"

        return consolidate_data

    def is_data_ready(self, report):
        for vendor in self.VENDORS_OF_INTEREST:
            result = report.get("data", {}).get("attributes", {}).get("results", {}).get(vendor)
            if not result:
                return False
        
        return True
    
    def get_flagged_count(self, results):
        PHISHING_INDICATOR = ['phishing', 'malware', 'malicious']
        phishing_count = sum(vendor['result'] in PHISHING_INDICATOR for vendor in results.values())
        return phishing_count

    def get_vendor_status(self, results):
        vendor_of_interest_status = {}
        for vendor in self.VENDORS_OF_INTEREST:
            if vendor in results:
                vendor_result = results[vendor]
                status = vendor_result['result']
                vendor_of_interest_status[vendor] = status.capitalize()
        
        return vendor_of_interest_status


    def extract_relevant_data_from_analysis_report(self, report):
        # Contains the status of each security vendor for the submitted url
        results = report["data"]["attributes"]["results"]
        num_of_vendors = len(results)

        # Get the number of vendors that flagged the url as red
        phishing_count = self.get_flagged_count(results)

        # Check the status of the 4 vendors we are interested in
        vendor_of_interest_status = self.get_vendor_status(results)

        vendors_flagged_red = f'="{phishing_count}/{num_of_vendors}"'

        print(vendors_flagged_red)
        print(vendor_of_interest_status)
        return vendors_flagged_red, vendor_of_interest_status
    
    def get_url_analysis_report(self, url_id, api_key):
        max_attempt = 10
        for attempt in range(max_attempt):
            response = requests.get(
                f'https://www.virustotal.com/api/v3/analyses/{url_id}',
                headers={'x-apikey': api_key}
            )

            report = response.json()
            is_interested_available = self.is_data_ready(report)

            if is_interested_available:
                # Extracts the relevant data that we are interested in
                return self.extract_relevant_data_from_analysis_report(report)

            time.sleep((attempt + 1) * 3)

    def get_url_validation_result(self, url_to_file_hash_dict, date, api_key):    
        validation_data = self.scan_url(url_to_file_hash_dict, api_key)
        ValidationUtils.generate_csv_report(validation_data, f"{date}_url_validation.csv")