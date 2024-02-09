import argparse
import json

import faulty_data_filter 
import categorize_data
import response_status_filter

LABEL_BOTH_FAULTY_TXT_FILE = "_dual_faulty_dataset.txt"
LABEL_SELF_REF_FAULTY_TXT_FILE = "_self_ref_only_faulty_dataset.txt"
LABEL_NO_REF_FAULTY_TXT_FILE = "_no_ref_only_faulty_dataset.txt"

FAULTY_DIR_BOTH = "faulty_both"
FAULTY_DIR_SELF = "faulty_self_ref"
FAULTY_DIR_NO = "faulty_no_ref"


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    parser.add_argument("dataset", help="Name of dataset folder path")
    parser.add_argument("date", help="Date of dataset")
    args = parser.parse_args()

    dateset_date = args.date
    dataset_path = args.dataset

    print("\nFinding faulty dataset...")
    total_dataset_count = faulty_data_filter.filter_faulty_dataset(dataset_path, dateset_date)
    
    print("\nCategorizing both faulty dataset...")
    num_of_both_faulty = categorize_data.categorize(dateset_date, dataset_path, f"{dateset_date}{LABEL_BOTH_FAULTY_TXT_FILE}", FAULTY_DIR_BOTH)
    print("\nCategorizing self ref only faulty dataset...")
    num_of_self_ref_faulty = categorize_data.categorize(dateset_date, dataset_path, f"{dateset_date}{LABEL_SELF_REF_FAULTY_TXT_FILE}", FAULTY_DIR_SELF)
    print("\nCategorizing no ref only faulty dataset...")
    num_of_no_ref_faulty = categorize_data.categorize(dateset_date, dataset_path, f"{dateset_date}{LABEL_NO_REF_FAULTY_TXT_FILE}", FAULTY_DIR_NO)
    
    print("\nCleaning up complete data...")
    num_of_complete = categorize_data.clean_up_complete_data(dataset_path)

    print("\nGetting response status")
    num_of_complete_200, num_of_complete_non_200 = response_status_filter.consolidate_reponse_status(dataset_path, dateset_date)
    
    count_num = {
        "Total number of dataset": total_dataset_count,
        "Number of complete dataset": num_of_complete,
        "Number of complete dataset with status code 200": num_of_complete_200,
        "Number of complete dataset with other status codes": num_of_complete_non_200,
        "Number of both (self ref & no ref) faulty dataset": num_of_both_faulty,
        "Number of self ref only faulty dataset": num_of_self_ref_faulty,
        "Number of no ref only faulty dataset": num_of_no_ref_faulty,
    }

    output_path = f"{dateset_date}_statistics.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(count_num, f, ensure_ascii=False, indent=4)