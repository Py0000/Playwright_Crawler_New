
import argparse
import json
import os
import zipfile
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import analyzer.feature_extraction as fe
from utils.file_utils import FileUtils
import utils.constants as Constants

class HtmlFeatureAnalyzer:
    headers = ["Date", "File Hash", "Length of HTML",
        "# Hidden Divs",
        "# Hidden Buttons",
        "# Hidden Inputs",
        "# Non-empty Links",
        "# empty links",
        "# Internal links", 
        "# External links",
        "# login forms",
        "# iframes",
        "# invisble iframes",
        "# semi invisible iframes",
        "# visible iframes",
        "# stylesheets",
        "# css stylesheets",
        "# internal resources",
        "# external resources"
    ]

    def __init__(self):
        pass

    def create_vector(self, soup, url):
        return {
            "Length of HTML": fe.len_html(soup),
            "# Hidden Divs": fe.hidden_div(soup),
            "# Hidden Buttons": fe.hidden_button(soup),
            "# Hidden Inputs": fe.hidden_input(soup),
            "# Non-empty Links": fe.number_of_links(soup),
            "# empty links": fe.empty_link(soup),
            "# Internal links": fe.internal_external_link(soup, url)[0], 
            "# External links": fe.internal_external_link(soup, url)[1],
            "# login forms": fe.login_form(soup),
            "# iframes": fe.num_of_iframes(soup),
            "# invisble iframes": fe.num_of_invisible_iframes(soup),
            "# semi invisible iframes": fe.num_of_semi_invisible_iframes(soup),
            "# visible iframes": fe.num_of_visible_iframes(soup),
            "# stylesheets": fe.num_of_stylesheets_total(soup),
            "# css stylesheets": fe.num_of_css_stylesheets(soup),
            "# internal resources": fe.internal_external_resource(soup, url)[0],
            "# external resources": fe.internal_external_resource(soup, url)[1]
        }
    
    def extract_html_features_info_from_individual_url(self, zip_ref, ref_type, csr_status, url):
        html_script_name = "html_script_bef.html" if csr_status == "before" else "html_script_aft.html"
        html_path = FileUtils.extract_file_path_from_zipped(zip_ref, ref_type, html_script_name)
        if html_path:
            with zip_ref.open(html_path) as html_file:
                html_content = html_file.read().decode('utf-8')
                soup = BeautifulSoup(html_content, "lxml")
                vector = self.create_vector(soup, url)
        
        return vector
    
    def analyze_date_specific_folder(self, dataset_folder, date, ref_type, csr_status):
        data = []
        for zip_file in tqdm(os.listdir(dataset_folder)):
            if not zip_file.endswith(".zip"):
                continue

            hash = zip_file.replace(".zip", "")
            zip_path = os.path.join(dataset_folder, zip_file)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                log_path = FileUtils.extract_file_path_from_zipped(zip_ref, ref_type, "log.json")
                url = ""
                if log_path:
                    with zip_ref.open(log_path) as log_file:
                        log_data = json.load(log_file)
                        url = log_data["Url visited"]
                
                feature_info = self.extract_html_features_info_from_individual_url(zip_ref, ref_type, csr_status, url)
                folder_info = {
                    "Date": date,
                    "File Hash": hash,
                    **feature_info
                }
                data.append(folder_info)

    def analyze_phishing(self, phishing_folder_path, ref_type, csr_status):
        consolidated_data = []
        for month in Constants.MONTHS:
            if month == "Oct":
                folders = Constants.PHISHING_FOLDERS_ALL_OCT
            if month == "Nov":
                folders = Constants.PHISHING_FOLDERS_ALL_NOV
            if month == "Dec":
                folders = Constants.PHISHING_FOLDERS_ALL_DEC
            
            for folder in tqdm(folders):
                dataset_folder = FileUtils.get_complete_phishing_dataset_parent_path(phishing_folder_path, month, folder)
                current_data = self.analyze_date_specific_folder(dataset_folder, folder, ref_type, csr_status)
                consolidated_data.append(current_data)
        
        return consolidated_data
    
    def export_data_to_excel(self, data, output_folder, domain_category):
        output_file = f"html_summary_{domain_category}.xlsx"  
        df = pd.DataFrame(data, columns=self.headers)
        df.to_excel(os.path.join(output_folder, output_file), index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extraction of html features info")
    parser.add_argument("folder", help="Input the folder that the dataset")
    parser.add_argument("result_path", help="Input the folder to store the results")
    parser.add_argument("phishing_mode", choices=["phishing", "benign"], help="Choose between phishing or benign")
    parser.add_argument("--ref_type", choices=["self_ref", "no_ref"], default="self_ref", help="Choose between self_ref or no_ref")
    parser.add_argument("--csr_status", choices=["after", "before"], default="after", help="Choose between self_ref or no_ref")
    parser.add_argument("domain_category", choices=Constants.DOMAIN_CATEGORIES, help="Phishing (state the month), Benign (Top 10k), Benign (less popular)?")
    args = parser.parse_args()

    html_feature_analyzer = HtmlFeatureAnalyzer()
    FileUtils.check_and_create_folder(args.result_path)

    if args.phishing_mode == "phishing":
        data = html_feature_analyzer.analyze_phishing(args.folder, args.ref_type, args.csr_status)
    elif args.phishing_mode == "benign":
        dataset_folder = FileUtils.get_complete_benign_dataset_parent_path(args.folder, Constants.BENIGN_DOMAIN_FOLDER_MAP.get(args.domain_category))
        data = html_feature_analyzer.analyze_date_specific_folder(dataset_folder, "benign", args.ref_type, args.csr_status)
    
    html_feature_analyzer.export_data_to_excel(data, args.result_path, args.domain_category)

    '''
    Example folder: datasets/all
    Example result_path: analyzer/html_info
    '''


        

       


