import argparse
import ast
import os
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


    def read_and_delete_duplicates(self, duplicate_txt_file):
        with open(duplicate_txt_file, "r") as file:
            for line in file:
                # Extract ZIP name and dates
                parts = line.split(" found on dates: ")
                zip_name = parts[0].replace("Duplicate ZIP folder: ", "").strip()
                dates = ast.literal_eval(parts[1].strip())
                # date_to_keep = dates[0]
                dates_to_delete = dates[1:]

                self.delete_duplicates(zip_name, dates_to_delete)   
            

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    parser.add_argument("txt_path", help="Duplicate Txt File Path")
    args = parser.parse_args()

    remover = DuplicateRemover()
    remover.read_and_delete_duplicates(args.txt_path)