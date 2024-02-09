import argparse
import hashlib
import csv 
import os


def filter_dataset_used_for_gpt_detection(csv_file, gpt_folder):
    matched_entries = []
    folder_names = {name.split('.zip')[0] for name in os.listdir(gpt_folder) if name.endswith('.zip')}
    # print(folder_names)

    with open(csv_file, mode='r', newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            print(row['SHA-256 Hash'] )
            print(row['SHA-256 Hash'] in folder_names)
            if row['SHA-256 Hash'] in folder_names:
                matched_entries.append(row)
    
    output_file = f"{csv_file.split('.')[0]}_used.csv"
    with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.DictWriter(csvfile, ['Url', 'SHA-256 Hash'])
        csv_writer.writeheader()
        for entry in matched_entries:
            csv_writer.writerow(entry)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    parser.add_argument("csv_path", help="csv name")
    parser.add_argument("gpt_folder_path", help="gpt folder name")
    args = parser.parse_args()

    filter_dataset_used_for_gpt_detection(args.csv_path, args.gpt_folder_path)