import os

from analyzer.utils import file_utils

class BlankPageFilter:
    def __init__(self, main_folder_path, date):
        self.main_folder_path = main_folder_path
        self.date = date


    def filter_out_blank_page_by_html(self, blank_page_list, ref_type):
        status = []

        date = self.date
        dataset_path = self.main_folder_path
        if "zip" in dataset_path:
            dataset_path = file_utils.extract_zipfile(dataset_path)

        parent_folder_path = os.path.join(dataset_path, f'dataset_{date}', f'dataset_{date}', 'complete_dataset')
        
        # Create the new directory to hold the dataset that contains the blank webpages
        blank_page_dir = os.path.join(parent_folder_path, 'blank_pages', ref_type)
        file_utils.check_and_generate_new_dir(blank_page_dir)


        for folder in blank_page_list:
            zip_dataset_path = os.path.join(parent_folder_path, f"{folder}.zip")
            print(zip_dataset_path)
            if (os.path.exists(zip_dataset_path)):
                print(folder, os.path.exists(zip_dataset_path), "moved")
                file_utils.shift_file_objects(zip_dataset_path, blank_page_dir)
            else:
                print(folder, os.path.exists(zip_dataset_path), "failed")
                status.append(folder) 
            
        log_dir = f"analyzer/blank_page/cat_logs/{date}"
        file_utils.check_and_generate_new_dir(log_dir)

        output_path = os.path.join(log_dir, f"{date}_{ref_type}_categorization_failed.txt")
        file_utils.export_output_as_txt_file(output_path, status)
        return output_path



class BlankPageFilterChecker:
    def __init__(self, primary_logs_dir, date):
        self.primary_logs_dir = primary_logs_dir
        self.date = date
        
    def cross_check_that_ss_is_blank(self, filtered_out_dataset, type):
        print("Cross checking that filtered files have blank screenshots...")
        status = {}
        date = self.date
        # Cross check against logs for screenshot
        ss_aft_blank_list = file_utils.read_data_from_txt_file_as_list(os.path.join(self.primary_logs_dir, f"{date}_ss_aft_blank_{type}.txt"))

        # Return a dict {dataset_name: {css: true/false, js: true/false, ss_aft: true/false}}
        for filtered in filtered_out_dataset:
            is_ss_aft_blank = False

            if filtered in ss_aft_blank_list:
                is_ss_aft_blank = True
            
            data = {
                "Is blank by ss (after)": is_ss_aft_blank
            }

            status[filtered] = data
        
        log_dir = f"analyzer/blank_page/cat_logs/{date}"
        output_path = os.path.join(log_dir, f"{date}_cat_cross_check_ss_{type}.json")
        file_utils.export_output_as_json_file(output_path, status)


    def potentially_ss_blank_not_filtered_yet(self, filtered_dataset, type):
        print("Checking if filtered files are also potentially blank by other file types...")
        date = self.date
        ss_aft_blank_list = file_utils.read_data_from_txt_file_as_list(os.path.join(self.primary_logs_dir, f"{date}_ss_aft_blank_{type}.txt"))

        # Remove from ss_aft blank list/log files those that are already filtered
        for filtered in filtered_dataset:
            if filtered in ss_aft_blank_list:
                ss_aft_blank_list.remove(filtered)

        # Return a new log with the remaining unfiltered ones
        log_dir = f"analyzer/blank_page/cat_logs/{date}"
        output_file = os.path.join(log_dir, f"{date}_unfiltered_extra_ss_blank_{type}.txt")
        file_utils.export_output_as_txt_file(output_file, ss_aft_blank_list)


