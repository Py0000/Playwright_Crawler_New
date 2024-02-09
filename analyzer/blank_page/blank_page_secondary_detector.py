import argparse
import os 
import zipfile

import cssutils
import warnings
import logging
import re

from analyzer.blank_page import blank_page_util
from analyzer.utils import file_utils

cssutils.log.setLevel(logging.CRITICAL)

class CssBlankDetector:

    @staticmethod
    # Check for css styles that renders the webpage blank
    def css_hide_content(css_content):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            sheet = cssutils.parseString(css_content)
            for rule in sheet:
                if rule.type == rule.STYLE_RULE:
                    if 'body' in rule.selectorText or 'html' in rule.selectorText:
                        for property in rule.style:
                            if property.name == 'display' and property.value == 'none' or property.name == 'visibility' and property.value == 'hidden':
                                return True
        return False


    def check_external_css(self, file):
        with open(file, 'r', encoding='utf-8') as css_file:
            css_content = css_file.read()
            if self.css_hide_content(css_content):
                print("CSS File that has potential blank element: ", file)
                return True


class JsBlankDetector:
    def js_hide_content(self, js_content):
        # Patterns that might indicate a blank page
        patterns = [
            re.compile(r'\bdocument\.body\.innerHTML\s*=\s*["\']\s*["\']', re.IGNORECASE),
            re.compile(r'\bdocument\.body\.style\.display\s*=\s*["\']none["\']', re.IGNORECASE),
            re.compile(r'\bdocument\.body\.style\.visibility\s*=\s*["\']hidden["\']', re.IGNORECASE),
            re.compile(r'\bdocument\.write\s*\(\s*["\']\s*["\']\s*\)', re.IGNORECASE),
            re.compile(r'\bdocument\.body\.outerHTML\s*=\s*["\']\s*["\']', re.IGNORECASE),
            re.compile(r'\bwhile\s*\(document\.body\.firstChild\)\s*document\.body\.removeChild\(document\.body\.firstChild\)', re.IGNORECASE),
        ]

        for pattern in patterns:
            if pattern.search(js_content):
                return True
        return False


    def check_external_js(self, file):
        with open(file, 'r', encoding='utf-8') as js_file:
            js_content = js_file.read()
            if self.js_hide_content(js_content):
                print("JavaScript file that potentially renders the page blank: ", file)
                return True
        

class BlankPageExternalDetector:
    def __init__(self, main_folder_path, date):
        self.main_folder_path = main_folder_path
        self.date = date

    
    # Recursively check external css scripts that renders the webpage blank
    def check_external_files(self, network_resp_path):
        potential_css = []
        is_css_blank = False
        potential_js = []
        is_js_blank = False

        css_detector = CssBlankDetector()
        js_detector = JsBlankDetector()

        for filename in os.listdir(network_resp_path):
            if filename.endswith('.css'):
                filepath = os.path.join(network_resp_path, filename)
                is_potentially_css_blank = css_detector.check_external_css(filepath)
                if is_potentially_css_blank:
                    potential_css.append(filename)
                    is_css_blank = True
            
            if filename.endswith('.js'):
                filepath = os.path.join(network_resp_path, filename)
                is_potentially_js_blank = js_detector.check_external_js(filepath)
                if is_potentially_js_blank:
                    potential_js.append(filename)
                    is_js_blank = True

        return is_css_blank, potential_css, is_js_blank, potential_js


    def check_external_resources_for_blank(self):
        main_directory = self.main_folder_path
        date = self.date
        consolidated_results = {}

        is_zip_file = "zip" in main_directory
        if is_zip_file:
            main_directory = file_utils.extract_zipfile(main_directory)
        
        parent_folder_path = os.path.join(main_directory, f'dataset_{date}', f'dataset_{date}', 'complete_dataset')
        for dir in os.listdir(parent_folder_path):
            current_dataset = dir.replace('.zip', '')
            current_dataset_dir = os.path.join(parent_folder_path, dir)

            with zipfile.ZipFile(current_dataset_dir, 'r') as zip_ref:
                zip_extraction_path = current_dataset_dir.replace('.zip', '')
                print(f"Extracting inner zip folder {dir}...")
                zip_ref.extractall(zip_extraction_path)
                current_dataset_dir = os.path.join(zip_extraction_path, current_dataset)
            
            dataset_status = {}
            for sub_dir in os.listdir(current_dataset_dir):
                try:
                    current_dataset_ref_dir = os.path.join(current_dataset_dir, sub_dir)
                    current_dataset_nw_resp_dir = os.path.join(current_dataset_ref_dir, 'network_response_files')
                    
                    is_blank_by_css, blank_css_list, is_blank_by_js, blank_js_list = self.check_external_files(current_dataset_nw_resp_dir)
                    
                    status = {
                        "CSS Style/Sheet": "Blank" if is_blank_by_css else "Not Blank",
                        "Potentially Blank CSS File": blank_css_list if is_blank_by_js else [],
                        "Js": "Blank" if is_blank_by_js else "Not Blank",
                        "Potentially Blank Js File": blank_js_list if is_blank_by_js else [],
                    }

                    dataset_status[sub_dir] = status
                
                except Exception as e:
                    print(e)
                    dataset_status[sub_dir] = "Error encountered while processing dataset folder"
                
            
            consolidated_results[current_dataset] = dataset_status
        
        base_output_dir = f"Analyzer/analysis/blank_page/primary_logs/secondary_logs/{date}"
        file_utils.check_and_generate_new_dir(base_output_dir)
        
        consolidated_output = os.path.join(base_output_dir, f"{date}_sec_consolidation.json")
        file_utils.export_output_as_json_file(consolidated_output)
        
        if is_zip_file:
            file_utils.remove_folder(main_directory)

        return consolidated_output
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    parser.add_argument("folder_path", help="Folder name")
    parser.add_argument("date", help="Date")
    args = parser.parse_args()

    external_resource_detector = BlankPageExternalDetector(args.folder_path, args.date)
    consolidated_output = external_resource_detector.check_external_resources_for_blank()

    base_output_dir = os.path.join("Analyzer/analysis/blank_page/secondary_logs", args.date)
    blank_page_util.split_log_files(consolidated_output, args.date, ["css", "js"], base_output_dir)
    