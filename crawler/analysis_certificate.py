import os
import json
import pandas as pd

import util
import util_def

# Helper function for summary-report generation.
# Helps to determine the range for the duration of cert validity for the webpages
def analyze_cert_duration_column(df, column, counts_dict):
    filtered_df = df.loc[df[column] != "Connection Error"]
    largest_value = filtered_df[column].max()
    smallest_value = filtered_df[column].min()
    range = str(smallest_value) + " to " + str(largest_value)
    counts_dict["Range"] = range

    return counts_dict

# Helper function for summary-report generation.
# Helps to determine the frequency of each field of interest
def analyze_other_columns(column, counts, counts_dict, consolidated_counts):
    # Find the highest count value
    max_count_value = counts.max()

    # Find all items with the highest count
    highest_count_items = counts[counts == max_count_value].index.tolist()

    if len(highest_count_items) == 1:
        highest_count_items = highest_count_items[0]
    else:
        # Convert the highest_count_items to a list of strings
        highest_count_items = [str(item) for item in highest_count_items]
        
    counts_dict["Most common item"] = highest_count_items

    # Include the highest count in the dictionary
    consolidated_counts[column] = counts_dict

    return consolidated_counts


# converts the json formateed cert data into a pandas dataframe
def extract_data_from_json(json_data):
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


# Consolidates all the certificate information of all the webpages crawled into a single excel.
def consolidate_cert_info_into_single_excel(ref_specific_dataset_path, ref_specific_analyzed_data_path):
    # Get all the sub-folders in the dataset/self_ref or dataset/no_ref folders
    # Each sub_folder contains information for each url link
    sub_folders = [d for d in os.listdir(ref_specific_dataset_path) if os.path.isdir(os.path.join(ref_specific_dataset_path, d))]
    df = pd.DataFrame()

    # Gets the cert info from the json file created during crawling, (from each folder - i.e. 0, 1, 2, .., etc)
    for sub_folder in sub_folders:
        cert_filepath = os.path.join(ref_specific_dataset_path, sub_folder, util_def.FILE_CERT)
        if os.path.exists(cert_filepath):
            with open(cert_filepath, 'r') as f:
                cert_json_data = json.load(f)
                current_df = extract_data_from_json(cert_json_data) # converts each cert json info into a pandas dataframe 
                df = pd.concat([df, current_df], ignore_index=True) # adds each dataframe into the consolidated dataframe
    
    output_path = os.path.join(ref_specific_analyzed_data_path, util_def.EXCEL_CERT_CONSOLIDATED)
    df.to_excel(output_path, index=False)


# Generates a summary of the certificate information for all webpages visited (in json format).
# Currently only summarizes: Cert-Issuer, Cert-valid-duration, SSL/TLS-protocol-ver, cert-sign-algo, cert-ver, cert-subj
def generate_consolidated_cert_summary_report(ref_specific_analyzed_data_path):
    consolidated_counts = {}
    data_path = os.path.join(ref_specific_analyzed_data_path, util_def.EXCEL_CERT_CONSOLIDATED)

    if os.path.exists(data_path):
        df = pd.read_excel(data_path)

        for column in df.columns:
            isCertIssuerOrg = column == "Certificate Issuer (Organization Name)"
            isCertDuration = column == "Certificate Valid Duration"
            isCertProtocol = column == "SSL/TLS Protocol Version"
            isCertSigAlgo = column == "Certificate Signature Algorithm"
            isCertVer = column == "Certificate Version"
            isCertCommonName = column == "Certificate Subject (Common Name)"
            
            if isCertIssuerOrg or isCertDuration or isCertProtocol or isCertSigAlgo or isCertVer or isCertCommonName:
                counts = df[column].value_counts()
                # Convert the Pandas Series to a dictionary before saving
                counts_dict = counts.to_dict()
                consolidated_counts[column] = counts_dict

                if isCertDuration: 
                    analyze_cert_duration_column(df, column, counts_dict)

                else:
                    analyze_other_columns(column, counts, counts_dict, consolidated_counts)
    
    output_path = os.path.join(ref_specific_analyzed_data_path, util_def.JSON_CERT_CONSOLIDATED)
    util.save_data_to_json_format(output_path, consolidated_counts)


def analyze_certificate_df(ref_specific_dataset_path, ref_specific_analyzed_data_path):
    consolidate_cert_info_into_single_excel(ref_specific_dataset_path, ref_specific_analyzed_data_path)
    generate_consolidated_cert_summary_report(ref_specific_analyzed_data_path)
    
