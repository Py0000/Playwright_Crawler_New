import argparse
import os

from analyzer.utils import file_utils

class BlockedPageFilter:
    def __init__(self, main_folder_path):
        self.main_folder_path = main_folder_path
        

    def get_seperate_list_of_blocked_data(self, txt_file):
        data = file_utils.read_data_from_json_file(txt_file)
        
        both = []
        self_ref = []
        no_ref = []

        for key, value in data.items():
            self_ref_value = value.get('self_ref')
            no_ref_value = value.get('no_ref')

            if self_ref_value != 200 and no_ref_value != 200:
                both.append(key)
            elif self_ref_value != 200:
                self_ref.append(key)
            elif no_ref_value != 200:
                no_ref.append(key)
        
        blocked_lists_dict = {
            "both": both,
            "self_ref": self_ref, 
            "no_ref": no_ref
        }

        return blocked_lists_dict


    def filter_blocked_page_by_category(self, date, parent_path, blocked_dir, cat, blocked_list):
        status = []

        blocked_sub_dir = os.path.join(blocked_dir, cat)
        file_utils.check_and_generate_new_dir(blocked_sub_dir)
        
        for folder in blocked_list:
            zip_dataset_path = os.path.join(parent_path, folder)
            if (os.path.exists(zip_dataset_path)):
                file_utils.shift_file_objects(zip_dataset_path, blocked_sub_dir)
            else:
                status.append(folder)
        
        blocked_page_cat_folder = os.path.join("Analyzer", "analysis", "block_page_cat_logs")
        file_utils.check_and_generate_new_dir(blocked_page_cat_folder)
        output_path = os.path.join(blocked_page_cat_folder, f"{date}_blocked_page_cat_failed.txt")
        file_utils.export_output_as_txt_file(output_path, status)


    def filter_blocked_page_main(self, date):
        main_directory = self.main_folder_path
        if "zip" in main_directory:
            main_directory = file_utils.extract_zipfile(main_directory)


        txt_parent_folder_path = os.path.join(main_directory, f'dataset_{date}', 'filter_logs')
        parent_path = os.path.join(main_directory, f'dataset_{date}', f'dataset_{date}', 'complete_dataset')
        blocked_dataset_txt_file_path = os.path.join(txt_parent_folder_path, f"{date}_response_non_200_status.json")
        blocked_lists_dict = self.get_seperate_list_of_blocked_data(blocked_dataset_txt_file_path)
        
        blocked_page_dir = os.path.join(parent_path, "blocked")
        file_utils.check_and_generate_new_dir(blocked_page_dir)
        
        blocked_cats = ["both", "self_ref", "no_ref"]
        for cat in blocked_cats:
            print(f"Filtering based on {cat}...")
            self.filter_blocked_page_by_category(date, parent_path, blocked_page_dir, cat, blocked_lists_dict.get(cat))
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    parser.add_argument("folder_path", help="Folder name")
    parser.add_argument("date", help="Date")
    args = parser.parse_args()

    block_page_filterer = BlockedPageFilter(args.folder_path)
    block_page_filterer.filter_blocked_page_main(args.date)