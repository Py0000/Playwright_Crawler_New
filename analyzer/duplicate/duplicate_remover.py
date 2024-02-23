import argparse
import ast
import os
import re
import shutil

class DuplicateRemover:
    def init(self):
        return
    
    def get_month_folder_from_date(self, date):
        month_mapping = {
            "10": "Oct",
            "11": "Nov",
            "12": "Dec"
        }

        month_part = date[2:4]
        return month_mapping.get(month_part)


    def delete_duplicates(self, zip_name, dates_to_delete):
        for date in dates_to_delete:
            month = self.get_month_folder_from_date(date)
            zip_folder_path = os.path.join("datasets", month, f"dataset_{date}", f"dataset_{date}", f"dataset_{date}", "complete_dataset", zip_name)
            os.remove(zip_folder_path)
            print(f"Deleted: {zip_folder_path}")


    def read_and_delete_url_duplicates(self, duplicate_txt_file):
        with open(duplicate_txt_file, "r") as file:
            for line in file:
                # Extract ZIP name and dates
                parts = line.split(" found on dates: ")
                zip_name = parts[0].replace("Duplicate ZIP folder: ", "").strip()
                dates = ast.literal_eval(parts[1].strip())
                # date_to_keep = dates[0]
                dates_to_delete = dates[1:]

                self.delete_duplicates(zip_name, dates_to_delete)   
    

    def read_html_duplicates(self, duplicate_txt_file):
        pattern = r'Duplicate for: (\d+): \[([^\]]+)\]'
        with open(duplicate_txt_file, "r") as file:
            content = file.read()
        matches = re.findall(pattern, content)
        date_zip_pairs = {}
        for match in matches:
            date = match[0]
            zip_files_str = match[1]
            zip_files = [zip_file.strip().strip("'\"") for zip_file in zip_files_str.split(', ')]

            date_zip_pairs[date] = zip_files
        
        return date_zip_pairs

    def remove_html_duplicates(self, info):
        for date, zip_folders in info.items():
            month = self.get_month_folder_from_date(date)
            for zip_folder in zip_folders:
                zip_folder_path = os.path.join("datasets", month, f"dataset_{date}", f"dataset_{date}", f"dataset_{date}", "complete_dataset", zip_folder)
                os.remove(zip_folder_path)
                print(f"Deleted: {zip_folder_path}")

    def read_and_delete_html_duplicates(self, duplicate_txt_file):
        date_zip_pairs = self.read_html_duplicates(duplicate_txt_file)
        self.remove_html_duplicates(date_zip_pairs)
        
        
            
            

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    parser.add_argument("txt_path", help="Duplicate Txt File Path")
    parser.add_argument("mode", help="url or html")
    args = parser.parse_args()

    remover = DuplicateRemover()
    if args.mode == "url":
        remover.read_and_delete_url_duplicates(args.txt_path)
    else:
        remover.read_and_delete_html_duplicates(args.txt_path)