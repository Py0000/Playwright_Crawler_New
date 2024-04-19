import argparse
import pandas as pd 

from analyzer.resource_analyzer import ResourceAnalyzer
import utils.constants as Constants
from utils.file_utils import FileUtils

class DNSAnalyzer(ResourceAnalyzer):
    NO_RECORDS_FLAG = "No records found"
    DNS_EXCEPTION = "DNS Exception occurred"
    ERROR_RESULTS = [[NO_RECORDS_FLAG], [DNS_EXCEPTION]]

    def __init__(self):
        pass

    def extract_data_from_json(self, json_data):
        domain = json_data.get("Domain", "")
        has_A_records = True if json_data.get("A") not in self.ERROR_RESULTS else False
        has_AAAA_records = True if json_data.get("AAAA") not in self.ERROR_RESULTS else False
        has_CAA_records = True if json_data.get("CAA") not in self.ERROR_RESULTS else False
        has_CNAME_records = True if json_data.get("CNAME") not in self.ERROR_RESULTS else False
        has_MX_records = True if json_data.get("MX") not in self.ERROR_RESULTS else False
        has_NS_records = True if json_data.get("NS") not in self.ERROR_RESULTS else False
        has_SOA_records = True if json_data.get("SOA") not in self.ERROR_RESULTS else False
        has_TXT_records = True if json_data.get("TXT") not in self.ERROR_RESULTS else False

        data = {
            "Domain": [domain],
            "has_A_records": [has_A_records],
            "has_AAAA_records": [has_AAAA_records],
            "has_CAA_records": [has_CAA_records],
            "has_CNAME_records": [has_CNAME_records],
            "has_MX_records": [has_MX_records],
            "has_NS_records": [has_NS_records],
            "has_SOA_records": [has_SOA_records],
            "has_TXT_records": [has_TXT_records],
        }

        df = pd.DataFrame(data)
        return df
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extraction of certifcate info")
    parser.add_argument("folder", help="Input the folder that the dataset")
    parser.add_argument("result_path", help="Input the folder to store the results")
    parser.add_argument("phishing_mode", choices=["phishing", "benign"], help="Choose between phishing or benign")
    parser.add_argument("--ref_type", choices=["self_ref", "no_ref"], default="self_ref", help="Choose between self_ref or no_ref")
    parser.add_argument("domain_category", choices=Constants.DOMAIN_CATEGORIES, help="Phishing (state the month), Benign (Top 10k), Benign (less popular)?")
    args = parser.parse_args()

    dns_analyzer = DNSAnalyzer()
    FileUtils.check_and_create_folder(args.result_path)

    if args.phishing_mode == "phishing":
        df = dns_analyzer.analyze_phishing(args.folder, args.ref_type, "dns.json")
    elif args.phishing_mode == "benign":
        dataset_folder = FileUtils.get_complete_benign_dataset_parent_path(args.folder, Constants.BENIGN_DOMAIN_FOLDER_MAP.get(args.domain_category))
        df = dns_analyzer.analyze_date_specific_folder(dataset_folder, args.ref_type, "dns.json")
    
    output_file_name = f"DNS_summary_{args.domain_category}.xlsx"
    dns_analyzer.export_data_to_excel(df, args.result_path, output_file_name)

    '''
    Example folder: datasets/all
    Example result_path: analyzer/certificate_info
    '''