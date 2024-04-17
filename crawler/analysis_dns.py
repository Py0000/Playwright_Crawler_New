import os
import json
import pandas as pd

import util
import util_def

NO_RECORDS_FLAG = "No records found"
DNS_EXCEPTION = "DNS Exception occurred"
ERROR_RESULTS = [[NO_RECORDS_FLAG], [DNS_EXCEPTION]]


# Get the number of true and false for each type of dns records for all webpages.
# I.e. returns the number of webpages that has a certain type of dns records (types are the column headers)
def get_true_false_count_DNS(df):
    true_counts = []
    false_counts = []

    for column in df.columns:
        if column == "Domain":
            true_counts.append("True Count:")
            false_counts.append("False Count:")
            continue

        true_count = df[column].eq("True").sum()
        false_count = df[column].eq("False").sum()
        true_counts.append(true_count)
        false_counts.append(false_count)
    
    return true_counts, false_counts


# Converts the json-formatted dns records info into a pandas dataframe
def extract_data_from_json(json_data):
    domain = json_data.get("Domain", "")
    has_A_records = True if json_data.get("A") not in ERROR_RESULTS else False
    has_AAAA_records = True if json_data.get("AAAA") not in ERROR_RESULTS else False
    has_CAA_records = True if json_data.get("CAA") not in ERROR_RESULTS else False
    has_CNAME_records = True if json_data.get("CNAME") not in ERROR_RESULTS else False
    has_MX_records = True if json_data.get("MX") not in ERROR_RESULTS else False
    has_NS_records = True if json_data.get("NS") not in ERROR_RESULTS else False
    has_SOA_records = True if json_data.get("SOA") not in ERROR_RESULTS else False
    has_TXT_records = True if json_data.get("TXT") not in ERROR_RESULTS else False

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


# Consolidates all the dns information of all the webpages crawled into a single excel.
def consolidate_dns_into_single_excel(ref_specific_dataset_path, ref_specific_analyzed_data_path):
    # Get all the sub-folders in the dataset/self_ref or dataset/no_ref folders
    # Each sub_folder contains information for each url link
    sub_folders = [d for d in os.listdir(ref_specific_dataset_path) if os.path.isdir(os.path.join(ref_specific_dataset_path, d))]
    df = pd.DataFrame()

    # Gets the cert info from the json file created during crawling, (from each folder - i.e. 0, 1, 2, .., etc)
    for sub_folder in sub_folders:
        dns_filepath = os.path.join(ref_specific_dataset_path, sub_folder, util_def.FILE_DNS)
        if os.path.exists(dns_filepath):
            with open(dns_filepath, 'r') as f:
                dns_json_data = json.load(f)
                current_df = extract_data_from_json(dns_json_data) # converts each dns json info into a pandas dataframe 
                df = pd.concat([df, current_df], ignore_index=True) # adds each dataframe into the consolidated dataframe
    
    output_path = os.path.join(ref_specific_analyzed_data_path, util_def.EXCEL_DNS_CONSOLIDATED)
    df.to_excel(output_path, index=False)



# Generates a summary of the dns records information for all webpages visited and update the excel file generated earlier.
# The excel file refers to the consolidated excel file.
def generate_consolidated_dns_summary_report(ref_specific_analyzed_data_path):
    data_path = os.path.join(ref_specific_analyzed_data_path, util_def.EXCEL_DNS_CONSOLIDATED)

    if os.path.exists(data_path):
        df = pd.read_excel(data_path, dtype=str)
        true_counts, false_counts = get_true_false_count_DNS(df)
        counts_df = pd.DataFrame([true_counts, false_counts], columns=df.columns)
        df = pd.concat([df, counts_df], ignore_index=True)
        df.to_excel(data_path, index=False)



def analyze_DNS_df(ref_specific_dataset_path, ref_specific_analyzed_data_path):
    consolidate_dns_into_single_excel(ref_specific_dataset_path, ref_specific_analyzed_data_path)
    generate_consolidated_dns_summary_report(ref_specific_analyzed_data_path)
    