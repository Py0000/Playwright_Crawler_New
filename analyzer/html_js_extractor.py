import argparse
import json
import os
import zipfile
from bs4 import BeautifulSoup
from tqdm import tqdm

from utils.file_utils import FileUtils
import utils.constants as Constants

class HtmlExtractor:
    def __init__(self):
        pass

    def extract_inline_javascript(self, html_content):
        scripts = []
        soup = BeautifulSoup(html_content, 'lxml')

        # Extract inline JavaScript
        for script in soup.find_all("script"):
            if not script.attrs.get("src"): # Inline JavaScript
                scripts.append(script.text)
        
        return scripts
    
    def extract_external_javascript(self, js_file):
        return js_file.read().decode('utf-8')
    

    def extract_from_individual_sample(self, zip_path, ref_type, csr_status):
        inline_scripts = []
        external_scripts = []

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            try:
                html_file_name = "html_script_aft.html" if csr_status.lower() == "after" else "html_script_bef.html"
                html_relative_path = FileUtils.extract_file_path_from_zipped(zip_ref, ref_type, html_file_name)
                html_path = next((zipinfo.filename for zipinfo in zip_ref.infolist() if html_relative_path in zipinfo.filename), None)
                if html_path:
                    with zip_ref.open(html_path) as html_file:
                        html_content = html_file.read().decode('utf-8')
                        inline_scripts = self.extract_inline_javascript(html_content)
                
                network_folder_name = ""
                network_resp_relative_dir = FileUtils.extract_file_path_from_zipped(zip_ref, ref_type, "network_response_files")
                is_exist = any(network_resp_relative_dir in zipinfo.filename for zipinfo in zip_ref.infolist())
                if is_exist:
                    network_resp_dir_path = next((zipinfo.filename for zipinfo in zip_ref.infolist() if network_resp_relative_dir in zipinfo.filename), None)
                    network_folder_name = "network_response_files/"
                else:
                    network_resp_relative_dir_alt = FileUtils.extract_file_path_from_zipped(zip_ref, ref_type, "network_data")
                    network_resp_dir_path = next((zipinfo.filename for zipinfo in zip_ref.infolist() if network_resp_relative_dir_alt in zipinfo.filename), None)
                    network_folder_name = "network_data/"

                for zipinfo in zip_ref.infolist():
                    # Check if the js file is in the network_response_files directory
                    if zipinfo.filename.startswith(network_resp_dir_path) and zipinfo.filename.endswith('.js'):
                        # Read each JS file and append its content to scripts
                            with zip_ref.open(zipinfo) as js_file:
                                js_name = zipinfo.filename.split(network_folder_name)[-1]
                                js_content = self.extract_external_javascript(js_file)
                                external_scripts.append({js_name: js_content})
            
            except Exception as e:
                print(e)
        
        return inline_scripts, external_scripts


    def analyse_date_specific_directory(self, dataset_folder, date, ref_type, csr_status, output_folder):
         for zip_file in tqdm(os.listdir(dataset_folder)):
            file_js_path = os.path.join(output_folder, date)
            if not os.path.exists(file_js_path):
                os.makedirs(file_js_path)
            
            if not zip_file.endswith(".zip"):
                continue

            hash = zip_file.replace(".zip", "")
            zip_path = os.path.join(dataset_folder, zip_file)
            inline_scripts, external_scripts = self.extract_from_individual_sample(zip_path, ref_type, csr_status)
            data = {
                "inline scripts": inline_scripts,
                "external scripts": external_scripts
            }

            output_file = os.path.join(output_folder, f"{hash}.json")
            FileUtils.save_as_json_output(output_file, data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extraction of javascript info from HTML files")
    parser.add_argument("folder", help="Input the folder that the dataset")
    parser.add_argument("result_path", help="Input the folder to store the results")
    parser.add_argument("phishing_mode", choices=["phishing", "benign"], help="Choose between phishing or benign")
    parser.add_argument("ref_type", choices=["self_ref", "no_ref"], default="self_ref", help="Choose between self_ref or no_ref")
    parser.add_argument("csr_status", choices=["after", "before"], default="after", help="Choose between after or before")
    args = parser.parse_args()

    extractor = HtmlExtractor()
    if args.phishing_mode == "phishing":
        for month in Constants.MONTHS:
            if month == 'Oct':
                folders = Constants.PHISHING_FOLDERS_ALL_OCT
            if month == 'Nov':
                folders = Constants.PHISHING_FOLDERS_ALL_NOV
            if month == 'Dec':
                folders = Constants.PHISHING_FOLDERS_ALL_DEC     

            result_path_tag = f"{args.ref_type}_{month}"
            for date in folders:
                try:
                    print(f"Extracting from {date}")
                    folder_path = FileUtils.get_complete_phishing_dataset_parent_path(args.folder, month, date)
                    result_folder = os.path.join(args.result_path, result_path_tag)
                    if not os.path.exists(result_folder):
                        os.makedirs(result_folder)
                    extractor.analyse_date_specific_directory(folder_path, date, args.ref_type, args.csr_status, result_folder)
                except Exception as e:
                    print(e)
    
    elif args.phishing_mode == "benign":
        for type in Constants.BENIGN_TYPES:
            if type == "top10k":
                folder = [Constants.BENIGN_FOLDER_ALL_TOP10K]
            if type == "100000_105000":
                folder = [Constants.BENIGN_FOLDER_ALL_100000_105000]
            
            result_path_tag = f"{args.ref_type}_{type}"
            try:
                print(f"Extracting from {type}")
                folder_path = FileUtils.get_complete_benign_dataset_parent_path(args.folder, folder)
                result_folder = os.path.join(args.result_path, result_path_tag)
                if not os.path.exists(result_folder):
                    os.makedirs(result_folder)
                extractor.analyse_date_specific_directory(folder_path, type, args.ref_type, args.csr_status, result_folder)
            except Exception as e:
                    print(e)
    
    '''
    Example folder path: datasets/all
    Example result path: analyzer/js_info
    '''

