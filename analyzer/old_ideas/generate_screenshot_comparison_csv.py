import json
import csv

def generate_csv_for_screenshot(json_data_file, file_hash_order_txt, date):
    # read the json data (that contains the hash differences)
    with open(json_data_file, 'r') as file:
        json_data = json.load(file)
        print("Json file loaded...")
    
    # Read the order of file hashes saved on the google sheet
    with open(file_hash_order_txt, 'r') as file:
        file_hash_order = [line.strip() for line in file]
        print("File hash order read...")
        print(f"{len(file_hash_order)} hashes read...")

    # Generate the csv report based on the order of file hashes
    csv_data = []
    for hash_key in file_hash_order:
        if hash_key in json_data:
            row = [hash_key] + list(json_data[hash_key].values())
            csv_data.append(row)
    
    headers = ["File Hash", "(Self Ref) pHash Difference", "(Self Ref) dHash Difference", "(No Ref) pHash Difference", "(No Ref) dHash Difference"]

    print(f"Size of csv_data: {len(csv_data)}")
    with open(f'{date}_screenshot_hash_comparison.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(csv_data)


