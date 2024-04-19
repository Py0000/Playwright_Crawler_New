import argparse
import requests

import utils
import url_scanner


def read_url_from_file(txt_file):
    with open(txt_file, 'r') as file:
        return [line.strip() for line in file if line.strip()]
    

# Submits url to be scan in VirusTotal
def scan_url(urls_list, api_key):
    consolidate_data = {}

    # VirusTotal API key (required to use the VirusTotal API)
    headers = {'x-apikey': api_key}

    # Loop through the selected url 
    count = 1
    for url in urls_list:
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
            vendors_flagged_red, vendor_of_interest_status = url_scanner.get_url_analysis_report(url_id, api_key)

            current_data = {
                "Website URL": url,
                "# Vendors Flagged Red": vendors_flagged_red,
                "OpenPhish": vendor_of_interest_status[url_scanner.VENDOR_OPENPHISH],
                "Google Safebrowsing": vendor_of_interest_status[url_scanner.VENDOR_GOOGLE_SAFEBROWSING],
                "Kaspersky": vendor_of_interest_status[url_scanner.VENDOR_KASPERSKY],
                "Trustwave": vendor_of_interest_status[url_scanner.VENDOR_KASPERSKY]
            }

            consolidate_data[count] = current_data
        
        else:
            print(f"URL: {url} - Error: {response.text}")
            consolidate_data[count] = f"Error: {response.text}"
        
        count = count + 1

    return consolidate_data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    parser.add_argument("txt_file", help="Name of the txt file that contains urls to validate")
    parser.add_argument("date", help="Date of dataset")
    args = parser.parse_args()

    api_key_file = 'virus_total_api_key.txt'
    api_key = utils.read_virus_total_api_key(api_key_file)

    urls_list = read_url_from_file(args.txt_file)
    data = scan_url(urls_list, api_key)
    utils.generate_csv_report(data, f"{args.date}_revalidation.csv")
