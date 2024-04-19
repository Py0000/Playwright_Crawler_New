import argparse
import pandas as pd 

from analyzer.resource_analyzer import ResourceAnalyzer
from utils.file_utils import FileUtils
import utils.constants as Constants

class CertificateAnalyzer(ResourceAnalyzer):
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

    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extraction of certifcate info")
    parser.add_argument("folder", help="Input the folder that the dataset")
    parser.add_argument("result_path", help="Input the folder to store the results")
    parser.add_argument("phishing_mode", choices=["phishing", "benign"], help="Choose between phishing or benign")
    parser.add_argument("ref_type", choices=["self_ref", "no_ref"], default="self_ref", help="Choose between self_ref or no_ref")
    parser.add_argument("domain_category", choices=Constants.DOMAIN_CATEGORIES, help="Phishing (state the month), Benign (Top 10k), Benign (less popular)?")
    args = parser.parse_args()

    certificate_analyzer = CertificateAnalyzer()
    FileUtils.check_and_create_folder(args.result_path)

    if args.phishing_mode == "phishing":
        df = certificate_analyzer.analyze_phishing(args.folder, args.ref_type, "cert.json")
    elif args.phishing_mode == "benign":
        dataset_folder = FileUtils.get_complete_benign_dataset_parent_path(args.folder, Constants.BENIGN_DOMAIN_FOLDER_MAP.get(args.domain_category))
        df = certificate_analyzer.analyze_date_specific_folder(dataset_folder, args.ref_type, "cert.json")
    
    output_file_name = f"Cert_summary_{args.domain_category}.xlsx"
    certificate_analyzer.export_data_to_excel(df, args.result_path, output_file_name)

    '''
    Example folder: datasets/all
    Example result_path: analyzer/certificate_info
    '''

            


