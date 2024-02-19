import argparse
import os
import re

from analyzer.utils import file_utils

def check_url_for_day(main_directory, date, urls_to_check):
    if "zip" in main_directory:
        main_directory = file_utils.extract_zipfile(main_directory)
    
    parent_folder_path = os.path.join(main_directory, f'dataset_{date}', f'dataset_{date}')
    feeds_txt_file = f"openphish_feeds_{date}.txt"

    feeds_file_path = os.path.join(parent_folder_path, feeds_txt_file)

    with open(feeds_file_path, "r") as file:
        file_urls = file.readlines()
        file_urls = [url.strip() for url in file_urls]

        for url in urls_to_check.keys():
            if url in file_urls:
                urls_to_check[url] = True
        

def main(main_dataset_dir):
    urls_to_check = {
        "hxxp://iv2fqbs1vdle-1322632174.cos.ap-jakarta.myqcloud.com/iv2fqbs1vdle.html": False,
        "hxxp://jhrr8kdc0p3o-1322632174.cos.ap-jakarta.myqcloud.com/jhrr8kdc0p3o.html": False,
        "hxxp://fe5macfepfr7-1322632174.cos.ap-singapore.myqcloud.com/fe5macfepfr7.html": False,
        "hxxp://jxjd0il2cxx6-1322632174.cos.ap-jakarta.myqcloud.com/jxjd0il2cxx6.html": False
    }

    months = ["Oct", "Nov", "Dec"]
    for month in months:
        month_folder_path = os.path.join(main_dataset_dir, month)
        folders = os.listdir(month_folder_path)

        for folder in folders:
            date = re.search(r"dataset_(\d+)", folder).group(1)
            check_url_for_day(os.path.join(month_folder_path, folder), date, urls_to_check)
    
    print(urls_to_check)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    parser.add_argument("folder_path", help="Folder name")
    args = parser.parse_args()

    main(args.folder_path)