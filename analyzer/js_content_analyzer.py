
import json
import os
from tqdm import tqdm
import pandas as pd

from utils.file_utils import FileUtils


class JsContentAnalyzer:
    def __init__(self):
        pass

    def extract_and_analyze_info(self, script_content):
        raise NotImplementedError("Subclasses should implement this method.")

    def combine_js_content(self, contents):
        scripts_content = '\n'.join(contents['inline scripts'])
        for external_script in contents['external scripts']:
            for script_content in external_script.values():
                scripts_content += '\n' + script_content
        
        return script_content

    def analyse_js_by_domain_category(self, js_info_folder, output_result_folder):
        for folder in tqdm(os.listdir(js_info_folder)):
            date_folder = os.path.join(js_info_folder, folder)
            current_date_output_folder = os.path.join(output_result_folder, folder)
            FileUtils.check_and_create_folder(current_date_output_folder)

            for json_file in tqdm(os.listdir(date_folder), desc=f"Processing {folder}"):
                hash = json_file.replace(".json", "")
                json_path = os.path.join(date_folder, json_file)

                try:
                    with open(json_path, 'r') as file:
                        data = json.load(file)
                    script_content = self.combine_js_content(data)

                    data = self.extract_and_analyze_info(script_content)
                    output_file = os.path.join(current_date_output_folder, f"{hash}.json")
                    FileUtils.save_as_json_output(output_file, data)
                except Exception as e:
                    print(e)
    
    def export_consolidated_to_excel(self, data, output_folder, output_file_name, header):
        df = pd.DataFrame(data)
        df = df[header]
        output_path = os.path.join(output_folder, output_file_name)
        df.to_excel(output_path, index=False)

