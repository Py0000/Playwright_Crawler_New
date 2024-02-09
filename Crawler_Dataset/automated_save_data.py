import time
import argparse

import new_data_reallocator


def shift_data_folder_periodically(folder_name, phishing_or_benign_tag):
    while True:
        time.sleep(360)
        new_data_reallocator.shift_data_from_Playwright_Crawler_folder(folder_name, phishing_or_benign_tag)
        



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Data shifting script.")
    parser.add_argument("folder_name", help="Name of the folder that contains the dataset")
    parser.add_argument("phishing_or_benign_tag", help="Name of the folder to store the dataset")
    args = parser.parse_args()

    shift_data_folder_periodically(args.folder_name, args.phishing_or_benign_tag)
