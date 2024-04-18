import argparse
import os
import json
import re
from tqdm import tqdm
import pandas as pd

from analyzer.js_content_analyzer import JsContentAnalyzer
import analyzer_utils
from utils.file_utils import FileUtils

class BrowserFingerprintAnalyzer(JsContentAnalyzer):
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
       


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Analysis of browser fingerprinting information")
    parser.add_argument("js_info_path", help="Input the folder that contains the javascript information")
    parser.add_argument("result_path", help="Input the folder to store the fingerprint results")
    parser.add_argument("domain_category", help="Phishing (state the month), Benign (Top 10k), Benign (less popular)?")
    args = parser.parse_args() 

    browser_fingerprint_analyzer = BrowserFingerprintAnalyzer()
    browser_fingerprint_analyzer.analyse_js_by_domain_category(args.js_info_path, args.result_path)
    consolidated_data = browser_fingerprint_analyzer.consolidate_fingerprint_results(args.result_folder)
    output_file_name = f"browser_fingerprint_summary_{args.domain_category}.xlsx"
    header = ["Date", "File Hash", "Total Num"] + analyzer_utils.top_basic_fingerprinting + analyzer_utils.top_advance_fingerprinting
    browser_fingerprint_analyzer.export_consolidated_to_excel(consolidated_data, args.result_path, output_file_name, header)

    '''
    Example js_info_path: analyzer/js_info
    Example result_path: analyzer/fingerprint_info
    '''