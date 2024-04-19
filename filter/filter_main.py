
import argparse
import os
from filter.faulty_data_filter import FaultyDataFilterer
from filter.response_status_filter import ResponseStatusFilterer
from utils.file_utils import FileUtils

class Filterer:
    def __init__(self):
        pass

    def filter(self, date_specific_dataset_folder, date):
        faulty_data_filter = FaultyDataFilterer()
        total_dataset_count = faulty_data_filter.filter_faulty_dataset(date_specific_dataset_folder, date)
        num_of_both_faulty = faulty_data_filter.categorize_faulty_data(date, date_specific_dataset_folder, os.path.join('filter', f"{date}_dual_faulty_dataset.txt"), "faulty_both")
        num_of_self_ref_faulty = faulty_data_filter.categorize_faulty_data(date, date_specific_dataset_folder, os.path.join('filter', f"{date}_self_ref_only_faulty_dataset.txt"), "faulty_self_ref")
        num_of_no_ref_faulty = faulty_data_filter.categorize_faulty_data(date, date_specific_dataset_folder, os.path.join('filter', f"{date}_no_ref_only_faulty_dataset.txt"), "faulty_no_ref")
        num_of_complete = faulty_data_filter.clean_up_complete_data(date_specific_dataset_folder)

        response_status_filter = ResponseStatusFilterer()
        num_of_complete_200, num_of_complete_non_200 = response_status_filter.consolidate_reponse_status(date_specific_dataset_folder, date)

        count_num = {
            "Total number of dataset": total_dataset_count,
            "Number of complete dataset": num_of_complete,
            "Number of complete dataset with status code 200": num_of_complete_200,
            "Number of complete dataset with other status codes": num_of_complete_non_200,
            "Number of both (self ref & no ref) faulty dataset": num_of_both_faulty,
            "Number of self ref only faulty dataset": num_of_self_ref_faulty,
            "Number of no ref only faulty dataset": num_of_no_ref_faulty,
        }

        output_path = os.path.join('filter', f"{date}_statistics.json")
        FileUtils.save_as_json_output(output_path, count_num)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    parser.add_argument("dataset", help="Name of dataset folder path")
    parser.add_argument("date", help="Date of dataset")
    args = parser.parse_args()

    filter = Filterer()
    filter.filter(args.dataset, args.date)