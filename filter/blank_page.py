import argparse
import cssutils
import logging
import os
import shutil
import warnings
import zipfile
from bs4 import BeautifulSoup
from tqdm import tqdm
from utils.file_utils import FileUtils

class CssBlankDetector:
    cssutils.log.setLevel(logging.CRITICAL)
    
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

class BlankPageDetector:
    BLANK_PAGE_LOG_FOLDER = os.path.join('filter', 'blank_page_logs')
    def __init__(self):
        FileUtils.check_and_create_folder(BlankPageDetector.BLANK_PAGE_LOG_FOLDER)

    def detect_blank_page_html_script(self, soup):
        # Analyze the body 
        body_content = soup.body.get_text(strip=True)

        inline_body_css = soup.find('style').string if soup.find('style') else ''
        is_inline_html_css_blank = CssBlankDetector.css_hide_content(inline_body_css)

        # Check if content of <body> is empty
        # And check if there are any child (direct) tags inside <body>
        if not body_content and len(soup.body.find_all(recursive=False)) == 0 or is_inline_html_css_blank:
            return True
        else:
            return False
    

    def process_individual_zipped_folder(self, zip_ref):
        dataset_status = {}
        for sub_dir in ["self_ref", "no_ref"]:
            try:
                html_bef_path = FileUtils.extract_file_path_from_zipped(zip_ref, sub_dir, "html_script_bef.html")
                html_aft_path = FileUtils.extract_file_path_from_zipped(zip_ref, sub_dir, "html_script_aft.html")
            
                with zip_ref.open(html_bef_path) as html_file_bef:
                    html_bef = html_file_bef.read().decode('utf-8')
                soup_bef = BeautifulSoup(html_bef, 'lxml')
                is_blank_by_html_bef = self.detect_blank_html_script(soup_bef)

                with zip_ref.open(html_aft_path) as html_file_aft:
                    html_aft = html_file_aft.read().decode('utf-8')
                soup_aft = BeautifulSoup(html_aft, 'lxml')
                is_blank_by_html_aft = self.detect_blank_html_script(soup_aft)

                status = {
                    "Html Script (Before)": "Blank" if is_blank_by_html_bef else "Not Blank",
                    "Html Script (After)": "Blank" if is_blank_by_html_aft else "Not Blank",
                }
                dataset_status[sub_dir] = status
            except Exception as e:
                dataset_status[sub_dir] = f"Error encountered: {e}"
        return dataset_status

    def analyze_date_specific_folder(self, complete_dataset_folder_path):
        consolidated_results = {}
        
        print("\nDetecting blank pages...")
        for zip_folder in tqdm(os.listdir(complete_dataset_folder_path)):
            if not zip_folder.endswith(".zip"):
                continue
            
            hash = zip_folder.replace('.zip', '')
            zip_file_path = os.path.join(complete_dataset_folder_path, zip_folder)
            with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
                dataset_stats = self.process_individual_zip_folder(zip_file)
                consolidated_results[hash] = dataset_stats
        
        return consolidated_results

    def save_detected_blank_page_as_txt(self, consolidated_results, date):
        both = []
        self_ref = []
        no_ref = []
        errors = []

        print("\nSaving blank pages info as txt...")
        for folder_name, content in consolidated_results.items():
            if (isinstance(content['self_ref'], dict) and isinstance(content['no_ref'], dict)):
                is_self_ref_blank = False
                is_no_ref_blank = False

                if content['self_ref'].get('Html Script (After)') == "Blank":
                    is_self_ref_blank = True
                if content['no_ref'].get('Html Script (After)') == "Blank":
                    is_no_ref_blank = True

                if is_self_ref_blank and is_no_ref_blank:
                    both.append(folder_name)
                elif is_self_ref_blank:
                    self_ref.append(folder_name)
                elif is_no_ref_blank:
                    no_ref.append(folder_name)
            if (isinstance(content['self_ref'], str) or isinstance(content['no_ref'], str)):
                errors.append(folder_name)
        

        both_output_file = os.path.join(BlankPageDetector.BLANK_PAGE_LOG_FOLDER, f"{date}_both.txt")
        self_ref_output_file = os.path.join(BlankPageDetector.BLANK_PAGE_LOG_FOLDER, f"{date}_self_ref.txt")
        no_ref_output_file = os.path.join(BlankPageDetector.BLANK_PAGE_LOG_FOLDER, f"{date}_no_ref.txt") 
        error_output_file = os.path.join(BlankPageDetector.BLANK_PAGE_LOG_FOLDER, f"{date}_error.txt") 
        FileUtils.save_as_txt_output(both_output_file, both)
        FileUtils.save_as_txt_output(self_ref_output_file, self_ref)    
        FileUtils.save_as_txt_output(no_ref_output_file, no_ref)
        FileUtils.save_as_json_output(error_output_file, errors)

        return both_output_file, self_ref_output_file, no_ref_output_file


class BlankPageFilterer:
    def __init__(self):
        FileUtils.check_and_create_folder(BlankPageDetector.BLANK_PAGE_LOG_FOLDER)

    def read_data_from_txt_file_as_list(self, txt_file):
        with open(txt_file, "r") as f: 
            data = f.readlines()

        # Remove newline characters and any whitespace
        data_list = [folder_name.strip() for folder_name in data]

        return data_list
    
    def filter_out_blank_page_by_html(self, complete_dataset_folder_path, blank_page_txt_file, ref_type, date):
        status = []
        new_blank_page_sub_dir = os.path.join(complete_dataset_folder_path, 'blank_pages', ref_type)
        FileUtils.check_and_create_folder(new_blank_page_sub_dir)

        blank_page_list = self.read_data_from_txt_file_as_list(blank_page_txt_file)
        print("\nFiltering out blank pages...")
        for folder in tqdm(blank_page_list):
            zip_dataset_path = os.path.join(complete_dataset_folder_path, f"{folder}.zip")
            if (os.path.exists(zip_dataset_path)):
                shutil.move(zip_dataset_path, new_blank_page_sub_dir)
            else:
                status.append(folder)
        
        if len(status) <= 0:
            output_file = os.path.join(BlankPageDetector.BLANK_PAGE_LOG_FOLDER, f'{date}_{ref_type}_categorization_failed.txt')
            FileUtils.save_as_json_output(output_file, status)


    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    parser.add_argument("folder_path", help="Folder name")
    parser.add_argument("month", help="Month")
    parser.add_argument("date", help="Date")
    parser.add_argument("phishing_mode", help="phishing or benign")
    args = parser.parse_args()

    if args.phishing_mode == "phishing":
        parent_folder_path = FileUtils.get_complete_phishing_dataset_parent_path(args.folder, args.month, args.date)
    else:
        parent_folder_path = FileUtils.get_complete_benign_dataset_parent_path(args.folder, args.month)

    detector = BlankPageDetector()
    consolidated_dict_detected = detector.analyze_date_specific_folder(parent_folder_path)
    both_file_name, self_ref_file_name, no_ref_file_name = detector.save_detected_blank_page_as_txt(consolidated_dict_detected, args.date)

    filterer = BlankPageFilterer()
    ref_types = ["both", "self_ref", "no_ref"]
    for ref_type in ref_types:
        if ref_type == 'both':
            txt_file_name = both_file_name
        elif ref_type == 'self_ref':
            txt_file_name = self_ref_file_name
        elif ref_type == 'no_ref':
            txt_file_name = no_ref_file_name
        
        filterer.filter_out_blank_page_by_html(parent_folder_path, txt_file_name, ref_type, args.date)
    
    

    

    
