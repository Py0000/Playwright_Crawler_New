import os
import requests
import time

from validation.utils import ValidationUtils

class HtmlScanner:
    def __init__(self):
        pass

    def scan_html_file(self, html_data_list, api_key):
        consolidate_data = []
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
                vendors_flagged_red = self.get_html_analysis_report(analysis_id, api_key)

                current_data = {
                    "File Hash": hash,
                    "Direct HTML Script Analysis by VirusTotal": vendors_flagged_red
                }

                consolidate_data.append(current_data)
            
            else:
                print(f"Error: {response.text}")
                consolidate_data.append({
                    "File Hash": hash,
                    "Direct HTML Script Analysis by VirusTotal": response.text
                })
            
            count += 1

        return consolidate_data
    
    def get_flagged_count(self, results):
        return sum(1 for vendor in results.values() if vendor['result'] is not None)

    def extract_total_value(self, report):
        # Contains the status of each security vendor for the submitted url
        results = report["data"]["attributes"]["results"]
        num_of_vendors = len(results)

        # Get number of vendors flagging the html file as red
        flagged_count = self.get_flagged_count(results)
        
        vendors_flagged_red = f'="{flagged_count}/{num_of_vendors}"'
        print(vendors_flagged_red)
        return vendors_flagged_red
    
    def get_html_analysis_report(self, analysis_id, api_key):
        max_attempt = 10
        for attempt in range(max_attempt):
            response = requests.get(
                f'https://www.virustotal.com/api/v3/analyses/{analysis_id}',
                headers={'x-apikey': api_key}
            )

            report = response.json()
            is_ready = report.get('data', {}).get('attributes', {}).get('status', 'unknown') == 'completed'
            if is_ready:
                return self.extract_total_value(report)
            else:
                time.sleep((attempt + 2) * 3)
    
    def get_html_validation_result(self, html_data_list, date, api_key):
        validation_data = self.scan_html_file(html_data_list, api_key)
        ValidationUtils.generate_csv_report(validation_data, f"{date}_html_verification.csv")