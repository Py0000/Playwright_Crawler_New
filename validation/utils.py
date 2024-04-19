import os
import csv

class ValidationUtils:
    @staticmethod
    # Read the VirusTotal API key from a txt file
    def read_virus_total_api_key(key_file):
        with open(key_file, 'r') as file:
            api_key = file.readline().strip()
        
        return api_key

    @staticmethod
    def generate_csv_report(validation_data_list, file_name):
        print("Generating CSV Report....")
        headers = validation_data_list[0].keys()

        with open(file_name, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(validation_data_list)

