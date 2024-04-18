import argparse
import os
import json
import re
from tqdm import tqdm
import pandas as pd

import analyzer_utils
from utils.file_utils import FileUtils

class BrowserFingerprintAnalyzer:
    def __init__(self):
        pass

    def search_for_basic_fingerprints(self, scripts_content):
        basic_fingerprinting_detected = {}
        for fingerprint in analyzer_utils.top_basic_fingerprinting:
            matches = re.findall(fingerprint.lower(), scripts_content.lower())
            if matches:
                basic_fingerprinting_detected[fingerprint] = len(matches)
        return basic_fingerprinting_detected
    
    def search_for_advance_fingerprints(self, scripts_content):
        adv_fingerprinting_detected = {}
        for fingerprint in analyzer_utils.top_advance_fingerprinting:
            matches = re.findall(fingerprint.lower(), scripts_content.lower())
            if matches:
                adv_fingerprinting_detected[fingerprint] = len(matches)
        return adv_fingerprinting_detected
    
    def search_and_combine_fingerprint_info(self, script_content):
        basic_fingerprinting_detected = self.search_for_basic_fingerprints(script_content)
        adv_fingerprinting_detected = self.search_for_advance_fingerprints(script_content)
        data = {
            "Basic fingerprints": basic_fingerprinting_detected,
            "Advanced fingerprints": adv_fingerprinting_detected
        }

        return data

    def consolidate_basic_fp(self, fingerprint_counts, file_data):
        basic_data = file_data.get('Basic fingerprints', {})
        basic_fp_count = 0
        for key in analyzer_utils.top_basic_fingerprinting:
            if key in basic_data:
                fingerprint_counts[key] = basic_data[key]
                basic_fp_count += basic_data[key]
        return basic_fp_count
    
    def consolidate_advance_fp(self, fingerprint_counts, file_data):
        advanced_data = file_data.get('Advanced fingerprints', {})
        advance_fp_count = 0
        for key in analyzer_utils.top_advance_fingerprinting:
            if key in advanced_data:
                fingerprint_counts[key] = advanced_data[key]
                advance_fp_count += advanced_data[key]
        return advance_fp_count

    def consolidate_fingerprint_results(self, fp_result_folder):
        data = []
        for folder in tqdm(os.listdir(fp_result_folder), desc=f"Consolidating fingerprint for {folder}"):
            folder_path = os.path.join(fp_result_folder, folder)
            if os.path.isdir(folder_path):
                for file in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file)
                    with open(file_path, 'r') as json_file:
                        file_data = json.load(json_file)
                    fingerprint_counts = {key: 0 for key in analyzer_utils.top_basic_fingerprinting + analyzer_utils.top_advance_fingerprinting}
                    
                    total_count = self.consolidate_basic_fp(fingerprint_counts, file_data)
                    total_count += self.consolidate_advance_fp(fingerprint_counts, file_data)

                    current_data = {
                        'Date': folder,
                        'File Hash': file.replace('.json', ''),
                        'Total Num': total_count,
                        **fingerprint_counts
                    }

                    data.append(current_data)
        return data
    
    def export_consolidated_to_excel(self, data, output_folder, domain_category):
        header = ["Date", "File Hash", "Total Num"] + analyzer_utils.top_basic_fingerprinting + analyzer_utils.top_advance_fingerprinting
        df = pd.DataFrame(data)
        df = df[header]
        output_path = os.path.join(output_folder, f"browser_fp_{domain_category}_summary.xlsx")
        df.to_excel(output_path, index=False)


