import argparse
import os
import re
import zipfile
import time
import random

import google.generativeai as genai

import PIL.Image
from baseline.gemini.gemini_request_helper import HtmlExtractor
from baseline.utils import utils

from utils.file_utils import FileUtils

class GeminiProVisionBaseline:
    def __init__(self, phishing_mode, use_html):
        self.phishing_mode = phishing_mode
        self.use_html = use_html
        self.html_extractor = HtmlExtractor()
        self.model = self.setup_model()
        
    def setup_model(self):
        genai.configure(api_key=utils.get_api_key("baseline/gemini/api_key_new.txt"))
        model = genai.GenerativeModel('gemini-pro-vision')
        return model
    
    def get_screenshot_path(self, zip_ref):
        screenshot_relative_path = os.path.join('self_ref', 'screenshot_aft.png')
        screenshot_exists = any(screenshot_relative_path in zipinfo.filename for zipinfo in zip_ref.infolist())
        screenshot_file_path = None
        if screenshot_exists:
            screenshot_file_path = next((zipinfo.filename for zipinfo in zip_ref.infolist() if screenshot_relative_path in zipinfo.filename), None)
        return screenshot_file_path
    
    def get_log_path(self, zip_ref):
        logs_relative_path = os.path.join('self_ref', 'log.json')
        log_exists = any(logs_relative_path in zipinfo.filename for zipinfo in zip_ref.infolist())
        log_file_path = None
        if log_exists:
            log_file_path = next((zipinfo.filename for zipinfo in zip_ref.infolist() if logs_relative_path in zipinfo.filename), None)
        return log_file_path
    
    def get_html_path(self, zip_ref):
        html_relative_path = os.path.join('self_ref', 'html_script_aft.html')
        html_exists = any(html_relative_path in zipinfo.filename for zipinfo in zip_ref.infolist())
        html_file_path = None
        if html_exists:
            html_file_path = next((zipinfo.filename for zipinfo in zip_ref.infolist() if html_relative_path in zipinfo.filename), None)
        return html_file_path
    
    def generate_full_model_prompt(self, few_shot_count, image, html_content):
        current_prediction_prompt = "Here is the webpage screenshot:"
        zero_shot_prompt, response_format_prompt = self.generate_zero_shot_prompt()
        few_shot_prompts = []
        for i in range(few_shot_count):
            example_prompt, example_image = self.generate_prompt_example(i + 1)
            few_shot_prompts.append(example_prompt)
            few_shot_prompts.append(example_image)
        
        if self.use_html:
            html_prompt = "\nHere are the info from the webpage html script:\n"
            model_prompt = [zero_shot_prompt] + few_shot_prompts + [current_prediction_prompt, image, html_prompt, html_content, response_format_prompt]

        else:
            model_prompt = [zero_shot_prompt] + few_shot_prompts + [current_prediction_prompt, image, response_format_prompt]

        return model_prompt

    def obtain_page_url(self, log_file):
        log_data = FileUtils.read_from_json_zipped_file(log_file)
        url = log_data["Url visited"]
        return url
    
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
        #return f"{system_prompt}", f"\n\n{reponse_format_prompt}"
    
    def generate_prompt_example(self, index):
        example_file_path = os.path.join("baseline", "gemini", "prompt_examples")
        image = PIL.Image.open(os.path.join(example_file_path, f"ss_{index}.png"))
        desc = FileUtils.read_from_txt_file(os.path.join(example_file_path, f"analysis_{index}.txt"))
    
        full_prompt = f"Below is an example analysis based on the provided image.\n{desc}"
        return full_prompt, image

    def analyse_individual_data(self, model, image, few_shot_count, folder_hash, html_content):
        try: 
            model_prompt = self.generate_full_model_prompt(few_shot_count, image, html_content)
            response = model.generate_content(model_prompt)
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
                hash = zip_file.split(".zip")[0]
                zip_path = os.path.join(zip_folder_path, zip_file)

                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    screenshot_file_path = self.get_screenshot_path(zip_ref)
                    if not screenshot_file_path:
                        continue

                    with zip_ref.open(screenshot_file_path) as screenshot_file:
                        html_content = None
                        if self.use_html:
                            html_file_path = self.get_html_path(zip_ref)
                            with zip_ref.open(html_file_path) as html_file:
                                html_content = html_file.read().decode('utf-8')
                                html_content = self.html_extractor.extract_relevant_info_from_html(html_content)
                        
                        image = PIL.Image.open(screenshot_file)
                        response = self.analyse_individual_data(self.model, image, few_shot_count, hash, html_content)
                    
                    log_file_path = self.get_log_path(zip_ref)
                    url = "Not found"
                    if log_file_path:
                        with zip_ref.open(log_file_path) as log_file:
                            url = self.obtain_page_url(log_file)

                    response.update({"Url": url})
                    responses.append(response)

                    time.sleep(random.randint(1, 3))
        
        output_file = f"baseline/gemini/gemini_responses/gemini_{date}_{few_shot_count}.json"
        FileUtils.save_as_json_output(output_file, responses)
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    #parser.add_argument("folder_path", help="Folder name")
    #parser.add_argument("date", help="Date")
    parser.add_argument("benign_phishing", help="benign or phishing")
    parser.add_argument("use_html", help="include html script in prompt?")
    args = parser.parse_args()

    phishing_folders = utils.phishing_folders_oct + utils.phishing_folders_nov + utils.phishing_folders_dec
    if args.benign_phishing == "benign":
        folders = utils.benign_folders
    else:
        folders = phishing_folders
       
    
    use_html = True if "html" in args.use_html else False
    gemini_baseline = GeminiProVisionBaseline(args.benign_phishing, use_html)
    for few_shot_count in ["0", "3"]:    
        for folder in folders:
            print(f"\n[{few_shot_count}-shot] Processing folder: {folder}")
            folder_path = os.path.join("baseline", "datasets", f"original_dataset_{folder}")
            date = folder
            gemini_baseline.analyse_directory(folder_path, date, int(few_shot_count))
            time.sleep(random.randint(10, 20))


   