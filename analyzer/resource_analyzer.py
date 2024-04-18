import os 
import json
import zipfile
import pandas as pd 
from tqdm import tqdm

from utils.file_utils import FileUtils
import utils.constants as Constants

class ResourceAnalyzer:
    def __init__(self):
        pass

    def extract_data_from_json(self, json_data):
        raise NotImplementedError("Subclasses should implement this method.")

    def analyze_date_specific_folder(self, date_folder_path, ref_type, file_name):
        df = pd.DataFrame()
        for zip_file in tqdm(os.listdir(date_folder_path)):
            if not zip_file.endswith(".zip"):
                continue

            zip_path = os.path.join(date_folder_path, zip_file)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                try:
                    file_path = FileUtils.extract_file_path_from_zipped(zip_ref, ref_type, file_name)
                    if file_path:
                        with zip_ref.open(file_path) as file:
                            json_data = json.load(file)
                        current_df = self.extract_data_from_json(json_data)
                        df = pd.concat([df, current_df], ignore_index=True)
                except Exception as e:
                    print(e)
        
        return df
    
    def analyze_phishing(self, phishing_folder_path, ref_type, file_name):
        consolidated_df = pd.DataFrame()
        for month in Constants.MONTHS:
            if month == "Oct":
                folders = Constants.PHISHING_FOLDERS_ALL_OCT
            if month == "Nov":
                folders = Constants.PHISHING_FOLDERS_ALL_NOV
            if month == "Dec":
                folders = Constants.PHISHING_FOLDERS_ALL_DEC
            
            for folder in tqdm(folders):
                dataset_folder = FileUtils.get_complete_phishing_dataset_parent_path(phishing_folder_path, month, folder)
                current_df = self.analyze_date_specific_folder(dataset_folder, ref_type, file_name)
                consolidated_df = pd.concat([consolidated_df, current_df], ignore_index=True)
        
        return consolidated_df
    
    def export_data_to_excel(self, df, output_path, output_file_name):
        output_file_path = os.path.join(output_path, output_file_name)
        df.to_excel(output_file_path, index=False)
    
