
import argparse
import os
import shutil
import zipfile

from tqdm import tqdm

from baseline.gemini.gemini_html_extractor import HtmlExtractor
from utils.file_utils import FileUtils

'''
Used to extract required assets from each samples for llm comparison experiment. 
'''
class InputSelector:
    def __init__(self, output_folder):
        self.target_output_folder = output_folder

    def extract_screenshot(self, zip_ref, hash_folder_path):
        screenshot_path = FileUtils.extract_file_path_from_zipped(zip_ref, 'self_ref', 'screenshot_aft.png')
        if screenshot_path:
            zip_ref.extract(screenshot_path, hash_folder_path)
            original_screenshot_path = os.path.join(hash_folder_path, screenshot_path)
            new_screenshot_path = os.path.join(hash_folder_path, f"screenshot_aft.png")
            shutil.copy(original_screenshot_path, new_screenshot_path)
            os.remove(original_screenshot_path)
            os.removedirs(os.path.dirname(original_screenshot_path))
    

    def extract_html_info(self, zip_ref):
        html_extractor = HtmlExtractor()
        html_path = FileUtils.extract_file_path_from_zipped(zip_ref, 'self_ref', 'html_script_aft.html')
        html_content = None
        if html_path:
            with zip_ref.open(html_path) as html_file:
                html = html_file.read().decode('utf-8')
                html_content = html_extractor.extract_relevant_info_from_html_to_string(html)
            
        return html_content
    

    def extract_url(self, zip_ref):
        log_path = FileUtils.extract_file_path_from_zipped(zip_ref, "self_ref", "log.json")
        url = "Not found"
        if log_path:
            with zip_ref.open(log_path) as log_file:
                log_data = FileUtils.read_from_json_zipped_file(log_file)
                url = log_data["Url visited"]
        return url


    def extract_assets(self, dataset_dir, date):
        target_path_folder = os.path.join(self.target_output_folder, date)
        
        dataset_folder = os.path.join(dataset_dir, f"original_dataset_{date}")
        saved_count = 0
        for folder in tqdm(os.listdir(dataset_folder)):
            if not folder.endswith(".zip"):
                continue

            folder_hash = folder.replace(".zip", "")
            hash_folder_path = os.path.join(target_path_folder, folder_hash)
            FileUtils.check_and_create_folder(hash_folder_path)
            with zipfile.ZipFile(os.path.join(dataset_folder, folder), 'r') as zip_ref:
                self.extract_screenshot(zip_ref, hash_folder_path)
                html_info = self.extract_html_info(zip_ref)
                url = self.extract_url(zip_ref)

                additional_info = {
                    "Url": url,
                    "html_brand_info": html_info
                }

                FileUtils.save_as_json_output(os.path.join(hash_folder_path, "add_info.json"), additional_info)
                saved_count += 1
        
        print(f"Saved Count: {saved_count}\nActual Count: {len(os.listdir(dataset_folder))}\n")



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract assets for LLM evaluations")
    parser.add_argument("folder", help="Input the folder that contains the dataset")
    parser.add_argument("date", help="Input the date of the dateset")
    parser.add_argument("result_path", help="Input the folder to store the results")
    args = parser.parse_args()

    if not os.path.exists(args.result_path):
        os.makedirs(args.result_path)

    input_selector = InputSelector(args.result_path)
    oct_dates = ['251023', '261023', '271023', '281023', '291023', '301023', '311023']
    nov_dates = ['011123', '041123', '051123', '061123', '071123', '081123', '091123', '101123', '111123', '121123', '131123', '141123', '151123', '161123', '171123', '181123', '191123', '201123', '211123', '221123', '231123', '241123', '251123', '261123', '271123', '281123', '291123', '301123']
    dec_dates = ['011223', '021223', '031223', '041223', '051223', '061223', '071223', '081223', '091223', '101223', '111223', '121223', '131223', '141223', '151223', '161223', '171223', '181223', '191223', '201223', '211223', '221223', '231223', '241223', '251223']
    dates = ['benign_1000', 'benign_2000', 'benign_101000']
    for date in dates:
        input_selector.extract_assets(args.folder, date)

                