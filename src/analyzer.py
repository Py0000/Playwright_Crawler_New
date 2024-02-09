import os

import analysis_certificate as ca
import analysis_dns as da
import analysis_features_extraction as fa

import analysis_dom_comparison as dom_comparison
import analysis_page_detector as page_detector
import analysis_screenshot_comparison as screenshot_comparison

import util
import util_def


def extract_and_analyse(dataset_folder_name, analyzed_data_folder_name, ref_flag):
    ref = util.get_crawled_dataset_base_folder_name(ref_flag)
    ref_specific_dataset_path = os.path.join(dataset_folder_name, ref)
    ref_specific_analyzed_data_path = os.path.join(analyzed_data_folder_name, ref)

    print(f"\nExtracting HTML features for {ref}...")
    fa.extract_features(ref_specific_dataset_path, ref_specific_analyzed_data_path)
    print(f"Done extractiing HTML features for {ref}...")

    print(f"Analysing Certificate Data for {ref}...")
    ca.analyze_certificate_df(ref_specific_dataset_path, ref_specific_analyzed_data_path)
    print(f"Done analysing Certificate Data for {ref}...")    

    print(f"Analysing DNS Data for {ref}...")
    da.analyze_DNS_df(ref_specific_dataset_path, ref_specific_analyzed_data_path)
    print(f"Done analysing DNS Data for {ref}...")


def analysis_page_for_differences(dataset_folder_name, analyzed_data_folder_name):
    dom_comparison.generate_dom_comparison_data(dataset_folder_name, analyzed_data_folder_name)
    page_detector.generate_page_analysis_report(dataset_folder_name, analyzed_data_folder_name)
    screenshot_comparison.generate_screenshot_comparison_report(dataset_folder_name, analyzed_data_folder_name)

