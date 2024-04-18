import argparse
import os 
import json
import zipfile
import pandas as pd 
from tqdm import tqdm

from utils.file_utils import FileUtils
import utils.constants as Constants

class CertificateAnalyzer:
    def __init__(self):
        pass

    def extract_data_from_json(self, json_data):
        data = {
            "Website": json_data.get("website url"),
            "Hostname": json_data.get("hostname"),
            "Certificate Subject (Common Name)": json_data.get("subject", {}).get("commonName", ""),
            "Certificate Subject (Organization)": json_data.get("subject", {}).get("organizationName", ""),
            "Certificate Subject (Locality or City)": json_data.get("subject", {}).get("localityName", ""),
            "Certificate Subject (State or Province)": json_data.get("subject", {}).get('stateOrProvinceName', ''),
            "Certificate Subject (Country)": json_data.get("subject", {}).get("countryName", ""),
            "Certificate Subject (Business Category)": json_data.get("subject", {}).get("businessCategory", ""),
            "Certificate Subject (Serial No.)": json_data.get("subject", {}).get("serialNumber", ""),
            "Certificate Subject (Jurisdiction State)": json_data.get("subject", {}).get("jurisdictionState", ""),
            "Certificate Subject (Jurisdiction Locality)": json_data.get("subject", {}).get("jurisdictionLocality", ""),
            "Certificate Issuer (Country Name)": json_data.get("issuer", {}).get("countryName", ""),
            "Certificate Issuer (Organization Name)": json_data.get("issuer", {}).get("organizationName", ""),
            "Certificate Issuer (Organizational Unit Name)": json_data.get("issuer", {}).get("organizationalUnitName", ""),
            "Certificate Issuer (Common Name)": json_data.get("issuer", {}).get("commonName", ""),
            "Certificate Version": json_data.get("version", ""),
            "Certificate Valid From": json_data.get("not_before", ""),
            "Certificate Valid Until": json_data.get("not_after", ""),
            "Certificate Valid Duration": json_data.get("valid_period", ""),
            "Certificate Serial Number": json_data.get("serial_number", ""),
            "Certificate Signature Algorithm": json_data.get("signature_algo", ""),
            "SSL/TLS Protocol Version": json_data.get("protocol_version", ""),
        }

        return pd.DataFrame([data])

    def analyse_date_specific_folder(self, date_folder_path, ref_type):
        df = pd.DataFrame()
        for zip_file in tqdm(os.listdir(date_folder_path)):
            if not zip_file.endswith(".zip"):
                continue

            zip_path = os.path.join(date_folder_path, zip_file)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                try:
                    cert_path = FileUtils.extract_file_path_from_zipped(zip_ref, ref_type, 'cert.json')
                    if cert_path:
                        with zip_ref.open(cert_path) as cert_file:
                            cert_json_data = json.load(cert_file)
                        
                        current_df = self.extract_data_from_json(cert_json_data)
                        df = pd.concat([df, current_df], ignore_index=True)
                except Exception as e:
                    print(e)
        
        return df
    
    def analyse_phishing(self, phishing_folder_path, ref_type):
        consolidated_df = pd.DataFrame()
        for month in Constants.MONTHS:
            if month == "Oct":
                folders = Constants.PHISHING_FOLDERS_ALL_OCT
            if month == "Nov":
                folders = Constants.PHISHING_FOLDERS_ALL_NOV
            if month == "Dec":
                folders = Constants.PHISHING_FOLDERS_ALL_DEC
            
            for folder in tqdm(folders):
                dataset_folder = FileUtils.get_complete_phishing_dataset_parent_path(phishing_folder_path, month, folder)
                current_df = self.analyse_date_specific_folder(dataset_folder, ref_type)
                consolidated_df = pd.concat([consolidated_df, current_df], ignore_index=True)
        
        return consolidated_df

    def export_data_to_excel(self, df, output_path, domain_category):
        output_file_path = os.path.join(output_path, f"Cert_info_summary_{domain_category}.xlsx")
        df.to_excel(output_file_path, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extraction of certifcate info")
    parser.add_argument("folder", help="Input the folder that the dataset")
    parser.add_argument("result_path", help="Input the folder to store the results")
    parser.add_argument("phishing_mode", choices=["phishing", "benign"], help="Choose between phishing or benign")
    parser.add_argument("ref_type", choices=["self_ref", "no_ref"], default="self_ref", help="Choose between self_ref or no_ref")
    parser.add_argument("domain_category", choices=Constants.DOMAIN_CATEGORIES, help="Phishing (state the month), Benign (Top 10k), Benign (less popular)?")
    args = parser.parse_args()

    certificate_analyzer = CertificateAnalyzer()

    if args.phishing_mode == "phishing":
        df = certificate_analyzer.analyse_phishing(args.folder, args.ref_type)
    elif args.phishing_mode == "benign":
        folder_name_map = {
            "top10k": Constants.BENIGN_FOLDER_ALL_TOP10K,
            "100000_105000": Constants.BENIGN_FOLDER_ALL_100000_105000
        } 
        dataset_folder = FileUtils.get_complete_benign_dataset_parent_path(args.folder, folder_name_map.get(args.domain_category))
        df = certificate_analyzer.analyse_date_specific_folder(dataset_folder, args.ref_type)
    
    certificate_analyzer.export_data_to_excel(df, args.result_path, args.domain_category)

    '''
    Example folder: datasets/all
    Example result_path: analyzer/certificate_info
    '''

            


