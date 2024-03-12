import argparse
import os
import re
import shutil
import zipfile
import time
import random

import google.generativeai as genai

import PIL.Image
from baseline.utils import utils

from utils.file_utils import FileUtils

class GeminiProVisionBaseline:
    def __init__(self, mode):
        self.mode = mode
        self.model = self.setup_model()
        
    def setup_model(self):
        genai.configure(api_key=utils.get_api_key("baseline/gemini/api_key.txt"))
        model = genai.GenerativeModel('gemini-pro-vision')
        return model
    
    def search_for_response(self, pattern, response_text):
        try: 
            return re.search(pattern, response_text).group(1).strip()
        except:
            return ""
    
    def format_model_response(self, folder_hash, response_text, is_error):
        if is_error:
            brand = has_credentials = has_call_to_actions = list_of_credentials = list_of_call_to_action = confidence_score = supporting_evidence = "Error Occurred"
        elif "payload size exceeds the limit" in response_text:
            brand = has_credentials = has_call_to_actions = list_of_credentials = list_of_call_to_action = confidence_score = supporting_evidence = "Payload exceeds limit"
        elif len(response_text) == 0:
            brand = has_credentials = has_call_to_actions = list_of_credentials = list_of_call_to_action = confidence_score = supporting_evidence = "Indeterminate"
        else: 
            brand = self.search_for_response(r'Brand: (.+)', response_text)
            has_credentials = self.search_for_response(r'Has_Credentials: (.+)', response_text)
            has_call_to_actions = self.search_for_response(r'Has_Call_To_Action: (.+)', response_text)
            list_of_credentials = self.search_for_response(r'List_of_credentials: (.+)', response_text)
            list_of_call_to_action = self.search_for_response(r'List_of_call_to_action: (.+)', response_text)
            confidence_score = self.search_for_response(r'Confidence_Score: (.+)', response_text)
            supporting_evidence = self.search_for_response(r'Supporting_Evidence: (.+)', response_text)

        return {
            "Folder Hash": folder_hash,
            "Brand": brand,
            "Has_Credentials": has_credentials,
            "Has_Call_To_Actions": has_call_to_actions,
            "List of Credentials fields": list_of_credentials,
            "List of Call-To-Actions": list_of_call_to_action,
            "Confidence Score": confidence_score,
            "Supporting Evidence": supporting_evidence
        }

    def generate_zero_shot_prompt(self):
        prompt_file_path = os.path.join("baseline", "gemini", "prompts")
        system_prompt = FileUtils.read_from_txt_file(os.path.join(prompt_file_path, "system_prompt.txt"))
        chain_of_thought_prompt = FileUtils.read_from_txt_file(os.path.join(prompt_file_path, "chain_of_thought_prompt.txt"))
        reponse_format_prompt = FileUtils.read_from_txt_file(os.path.join(prompt_file_path, "response_format_prompt.txt"))

        return f"{system_prompt}\n\n{chain_of_thought_prompt}", f"\n\n{reponse_format_prompt}"
    
    def generate_prompt_example(self, index):
        example_file_path = os.path.join("baseline", "gemini", "prompt_examples")
        image = PIL.Image.open(os.path.join(example_file_path, f"ss_{index}.png"))
        desc = FileUtils.read_from_txt_file(os.path.join(example_file_path, f"analysis_{index}.txt"))
    
        full_prompt = f"Below is an example analysis based on the provided image.\n{desc}"
        return full_prompt, image

    def analyse_individual_data(self, model, image_path, few_shot_count):
        zero_shot_prompt, response_format_prompt = self.generate_zero_shot_prompt()
        few_shot_prompts = []
        for i in range(few_shot_count):
            example_prompt, example_image = self.generate_prompt_example(i + 1)
            few_shot_prompts.append(example_prompt)
            few_shot_prompts.append(example_image)

        current_prediction_prompt = "Here is the webpage screenshot:"
        try: 
            image = PIL.Image.open(image_path)
            folder_hash = image_path.split("/")[3]
            model_prompt = [zero_shot_prompt] + few_shot_prompts + [current_prediction_prompt, image, response_format_prompt]
            response = model.generate_content(model_prompt, stream=True)
            response.resolve()
            data = self.format_model_response(folder_hash, response.text, is_error=False)
            return data
        except Exception as e:
            data = self.format_model_response(folder_hash, str(e), is_error=True)
            print(e)
            return data


    def analyse_directory(self, zip_folder_path, date, few_shot_count):
        responses = []

        for zip_file in os.listdir(zip_folder_path):
            print(f"Processing {zip_file}")
            
            if zip_file.endswith(".zip"):
                zip_path = os.path.join(zip_folder_path, zip_file)

                # Extract the zip file
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    extract_path = os.path.join(zip_folder_path, zip_file.replace('.zip', ''))
                    zip_ref.extractall(extract_path)
                    
                    if self.mode == "phishing":
                        self_ref_path = os.path.join(extract_path, extract_path.split("/")[3], 'self_ref')
                    else: 
                        self_ref_path = os.path.join(extract_path, 'self_ref')
                    
                    # Find the screenshot in the extracted folder
                    if os.path.exists(self_ref_path):
                        screenshot_path = os.path.join(self_ref_path, 'screenshot_aft.png')

                        if not os.path.exists(screenshot_path):
                            continue

                        response = self.analyse_individual_data(self.model, screenshot_path, few_shot_count)
                        responses.append(response)
                    
                    # Delete the extracted folder after processing
                    shutil.rmtree(extract_path)
        
        output_file = f"baseline/gemini/gemini_responses/gemini_{date}_{few_shot_count}.json"
        FileUtils.save_as_json_output(output_file, responses)
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    #parser.add_argument("folder_path", help="Folder name")
    #parser.add_argument("date", help="Date")
    parser.add_argument("benign_phishing", help="benign or phishing")
    parser.add_argument("few_shot_count", help="number of examples to include")
    args = parser.parse_args()

    benign_folders = ["benign_1000"]
    phishing_folders_oct = ["251023", "261023", "271023", "281023", "291023", "301023", "311023"] # oct
    phishing_folders_nov = ["011123", "041123", "051123", "061123", "071123", "081123", "091123", "101123", "111123", "121123", "131123", "141123", "151123", "161123", "171123", "181123", "191123", "201123", "211123", "221123", "231123", "241123", "251123", "261123", "271123", "281123", "291123", "301123"]
    phishing_folders_dec = ["011223", "021223", "031223", "041223", "051223", "061223", "071223", "081223", "091223", "101223", "111223", "121223", "131223", "141223", "151223", "161223", "171223", "181223", "191223", "201223", "211223", "221223", "231223", "241223", "251223"]
    phishing_folders = phishing_folders_oct + phishing_folders_nov + phishing_folders_dec
    
    if args.benign_phishing == "benign":
        folders = benign_folders
    else:
        folders = phishing_folders
    
    gemini_baseline = GeminiProVisionBaseline(args.benign_phishing)
    for folder in folders:
        print(f"\nProcessing folder: {folder}")
        folder_path = os.path.join("baseline", "datasets", f"original_dataset_{folder}")
        date = folder
        gemini_baseline.analyse_directory(folder_path, date, int(args.few_shot_count))
        time.sleep(random.randint(10, 20))


   