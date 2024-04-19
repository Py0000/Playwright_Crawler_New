
import argparse
import os
import zipfile
import pandas as pd
from tqdm import tqdm

import utils.constants as Constants
from utils.file_utils import FileUtils

class NetworkPayloadAnalyzer:
    def __init__(self):
        pass

    def track_network_payload_for_individual_url(self, zip_ref, network_payload_folder, ref_type, folder_info):
        formatted_network_payload_folder = f"{network_payload_folder}/"
        network_resp_files = [zipinfo for zipinfo in zip_ref.infolist() if ref_type in zipinfo.filename and formatted_network_payload_folder in zipinfo.filename and not zipinfo.is_dir()]
        for zipinfo in network_resp_files:
            _, ext = os.path.splitext(zipinfo.filename)
            if ext.lower() in folder_info.keys():
                folder_info[ext.lower()] += 1
            else:
                folder_info[ext.lower()] = 1
    
    def analyze_date_specific_folder(self, dataset_folder, date, network_payload_folder, ref_type):
        data = []
        for zip_file in tqdm(os.listdir(dataset_folder)):
            if not zip_file.endswith(".zip"):
                continue

            hash = zip_file.replace(".zip", "")
            zip_path = os.path.join(dataset_folder, zip_file)
            folder_info = {
                "Date": date,
                "File Hash": hash
            }

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                try:
                    self.track_network_payload_for_individual_url(zip_ref, network_payload_folder, ref_type, folder_info)
                except Exception as e:
                    print(e)
            data.append(folder_info)

        return data
    
    def analyze_phishing(self, phishing_folder_path, network_payload_folder, ref_type):
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
                current_data = self.analyze_date_specific_folder(dataset_folder, folder, network_payload_folder, ref_type)
                consolidated_data.append(current_data)
        
        return consolidated_data

    def export_network_info_as_excel(self, data, output_folder, domain_category):
        df = pd.DataFrame(data)
        df.fillna(0, inplace=True)
        for col in df.columns[2:]:
            df[col] = df[col].astype(int)
        output_file = os.path.join(output_folder, f"network_summary_{domain_category}.xlsx")
        df.to_excel(output_file, index=False)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extraction of network payload info")
    parser.add_argument("folder", help="Input the folder that the dataset")
    parser.add_argument("result_path", help="Input the folder to store the results")
    parser.add_argument("phishing_mode", choices=["phishing", "benign"], help="Choose between phishing or benign")
    parser.add_argument("network_payload_folder", help="Input the folder name that contains the network payloads")
    parser.add_argument("ref_type", choices=["self_ref", "no_ref"], default="self_ref", help="Choose between self_ref or no_ref")
    parser.add_argument("domain_category", choices=Constants.DOMAIN_CATEGORIES, help="Phishing (state the month), Benign (Top 10k), Benign (less popular)?")
    args = parser.parse_args()

    network_payload_analyzer = NetworkPayloadAnalyzer()
    FileUtils.check_and_create_folder(args.result_path)

    if args.phishing_mode == "phishing":
        data = network_payload_analyzer.analyze_phishing(args.folder, args.network_payload_folder, args.ref_type)
    elif args.phishing_mode == "benign":
        dataset_folder = FileUtils.get_complete_benign_dataset_parent_path(args.folder, Constants.BENIGN_DOMAIN_FOLDER_MAP.get(args.domain_category))
        data = network_payload_analyzer.analyze_date_specific_folder(dataset_folder, args.network_payload_folder, args.ref_type)
    
    network_payload_analyzer.export_network_info_as_excel(data, args.result_path, args.domain_category)

    '''
    Example folder: datasets/all
    Example result_path: analyzer/network_info
    Example network_payload_folder: network_response_files or network_data
    '''