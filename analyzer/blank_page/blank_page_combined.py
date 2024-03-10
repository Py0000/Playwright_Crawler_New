import argparse
import os

from analyzer.blank_page import blank_page_detector
from analyzer.blank_page import blank_page_filter
from analyzer.blank_page import blank_page_util
from analyzer.utils import file_utils

class BlankPageHandler:
    def __init__(self, main_folder_path, date, mode):
        self.main_folder_path = main_folder_path
        self.date = date
        self.mode = mode
    
    """
    def shift_detector_log_files(self, src_dir):
        print(f"Shifting {src_dir} log files...")
        date = self.date
        logs_dir = os.path.join(f"dataset_{date}", f"dataset_{date}", f"dataset_{date}", "complete_dataset", "blank_pages", "logs", src_dir)
        file_utils.check_and_generate_new_dir(logs_dir)

        for file in os.listdir(os.path.join(src_dir, date)):
            src_file_path = os.path.join(os.path.join(src_dir, date), file)
            if os.path.exists(src_file_path):
                dest_file_path = os.path.join(logs_dir, file)
                file_utils.shift_file_objects(src_file_path, dest_file_path)
            else:
                print(f"File {file} does not exist!")


    def clean_up_logs(self):
        base_folder = f"Analyzer/analysis/blank_page"
        log_files_folder = [f'primary_logs', f'cat_logs']
        for folder in log_files_folder:
            self.shift_detector_log_files(os.path.join(base_folder, folder))
    """

    def detect_blank_page(self):
        date = self.date
        detector = blank_page_detector.BlankPageDetector(self.main_folder_path, date, self.mode)
        consolidated_detector_output = detector.check_dataset_for_blank()

        blank_page_output_dir = os.path.join("analyzer/blank_page/primary_logs", date)
        blank_page_util.split_log_files(consolidated_detector_output, date, ["html", "ss_aft", "ss_bef"], blank_page_output_dir)
        detector.get_error_logs(consolidated_detector_output, blank_page_output_dir)
    

    def filter_blank_page(self, ref_type):
        date = self.date
        primary_logs_dir = os.path.join("analyzer/blank_page/primary_logs", date)
        filterer = blank_page_filter.BlankPageFilter(self.main_folder_path.replace(".zip", ""), date, self.mode)
        checker = blank_page_filter.BlankPageFilterChecker(primary_logs_dir, date)

        html_blank_txt_file_path = os.path.join(primary_logs_dir, f"{date}_html_blank_{ref_type}.txt")
        blank_page_by_html_list = file_utils.read_data_from_txt_file_as_list(html_blank_txt_file_path)

        unsuccessful_filtered_path = filterer.filter_out_blank_page_by_html(blank_page_by_html_list, ref_type)
        unsuccessful_filtered = file_utils.read_data_from_txt_file_as_list(unsuccessful_filtered_path)
        filtered = [item for item in blank_page_by_html_list if item not in unsuccessful_filtered]
        checker.cross_check_that_ss_is_blank(filtered, ref_type)
        checker.potentially_ss_blank_not_filtered_yet(filtered, ref_type)
    

    def detect_and_filter(self):
        self.detect_blank_page()

        ref_types = ["both", "self_ref", "no_ref"]
        for ref_type in ref_types:
            self.filter_blank_page(ref_type)
        
        #self.clean_up_logs()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    parser.add_argument("folder_path", help="Folder name")
    parser.add_argument("date", help="Date")
    parser.add_argument("mode", help="phishing or benign")
    args = parser.parse_args()

    blank_page_handler = BlankPageHandler(args.folder_path, args.date, args.mode)
    blank_page_handler.detect_and_filter()





