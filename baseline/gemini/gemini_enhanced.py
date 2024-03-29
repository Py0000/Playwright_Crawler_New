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
    def __init__(self, phishing_mode, mode):
        self.phishing_mode = phishing_mode
        self.mode = mode
        self.html_extractor = HtmlExtractor()
        self.model = self.setup_model()
        
    def setup_model(self):
        genai.configure(api_key=utils.get_api_key("baseline/gemini/api_key_new.txt"))
        if self.mode == "ss" or self.mode == "both":
            model = genai.GenerativeModel('gemini-pro-vision')
        elif self.mode == "html":
            model = genai.GenerativeModel('gemini-pro')
            
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
        if self.mode == "ss":
            system_prompt_txt_file = "system_prompt_ss.txt"
            reponse_format_txt_file = "response_format_prompt.txt"
        elif self.mode == "html":
            system_prompt_txt_file = "system_prompt_html.txt"
            reponse_format_txt_file = "response_format_prompt_html.txt"
        elif self.mode == "both":
            system_prompt_txt_file = "system_prompt_both.txt"
            reponse_format_txt_file = "response_format_prompt.txt"

        system_prompt = FileUtils.read_from_txt_file(os.path.join(prompt_file_path, system_prompt_txt_file))
        chain_of_thought_prompt = FileUtils.read_from_txt_file(os.path.join(prompt_file_path, "chain_of_thought_prompt.txt"))
        reponse_format_prompt = FileUtils.read_from_txt_file(os.path.join(prompt_file_path, reponse_format_txt_file))

        return f"{system_prompt}\n\n{chain_of_thought_prompt}", f"\n\n{reponse_format_prompt}"
        #return f"{system_prompt}", f"\n\n{reponse_format_prompt}"
    
    def generate_prompt_example(self, index):
        img_1_desc = "The screenshot prominently displays the Outlook logo, consisting of an O and an envelope, which is the widely recognized symbol for Microsoft's Outlook email service. The word Outlook is also displayed next to the logo, further confirming the brand identity. Below the logo, there are two fields, labeled in Chinese characters, which translate to Email and Password, respectively. These are the standard credential fields for logging into an email service. There is also a call-to-action present, in the form of a sign in link/button, which is stylized with the Outlook branding colors and an accompanying icon. The confidence in brand identification is absolute due to the unmistakable Outlook logo and clear branding elements that match Microsoft's design language for its email service. Additionally, the layout, typography, and style are consistent with Outlook's official login page. There is no conflicting branding or elements that would suggest any other brand is represented on this page."
        img_2_desc = "The screenshot displays the AT&T logo prominently at the top, which is the main factor in identifying the brand. This logo is a well-known trademark of AT&T, a large telecommunications company. Under the logo, there is a sign-in form with fields for Email and Password, indicating that the webpage is asking for user credentials. Just below the credential fields is a SIGN IN button, which serves as the call-to-action element. It prompts the user to proceed with the action of signing into their account. My confidence in identifying the brand is high due to the clear visibility of the AT&T logo, but not absolute because there's always a possibility of webpage spoofing or use of the logo in a third-party context (e.g., a service portal for AT&T services created by a different company). There is no evidence of other brands being primary on this page. The presence of the 'weebly.' at the bottom suggests that the webpage may have been created using the Weebly website-building platform, which does not necessarily affect the identification of the primary brand represented in the screenshot. The design of the sign-in form is straightforward, with no additional elements that might suggest a different brand or service."
        img_3_desc = "The screenshot showcases the Meta logo, which is the parent company of Facebook. The logo is located at the top left corner of the page. Although there are other logos from Twitter, Instagram and Linkedin, but the brand associated with this page is Facebook."

        html_1_desc = "The HTML title states that it is Outlook."
        html_2_desc = "The HTML title states that it is the login page of AT&T. Although the favicon is from weebly, this highly suggest that this AT&T page is built using Weebly website builder."
        html_3_desc = "The HTML title states that it is Meta, the footer confirms that this is Meta, the parent company of Facebook."

        img_descs = [img_1_desc, img_2_desc, img_3_desc]
        html_descs = [html_1_desc, html_2_desc, html_3_desc]

        example_file_path = os.path.join("baseline", "gemini", "prompt_examples")
        image = PIL.Image.open(os.path.join(example_file_path, f"ss_{index}.png"))
        desc = FileUtils.read_from_txt_file(os.path.join(example_file_path, f"analysis_{index}.txt")) 

        if self.mode == "ss":
            desc = desc + img_descs[index-1]
        elif self.mode == "html":
            desc = desc + html_descs[index-1]
        elif self.mode == "both":
            desc = desc + img_descs[index-1] + " " + html_descs[index-1]
    
        full_prompt = f"Below is an example analysis.\n{desc}"
        return full_prompt, image
    
    def generate_full_model_prompt(self, few_shot_count, image, html_content):
        current_prediction_prompt = "Here is the webpage screenshot:"
        zero_shot_prompt, response_format_prompt = self.generate_zero_shot_prompt()
        few_shot_prompts = []
        for i in range(few_shot_count):
            example_prompt, example_image = self.generate_prompt_example(i + 1)
            few_shot_prompts.append(example_prompt)
            
            if self.mode == "ss" or self.mode == "both":
                few_shot_prompts.append(example_image)
        
        html_prompt = "\nHere are the info from the webpage html script:\n"
        if self.mode == "both":
            model_prompt = [zero_shot_prompt] + few_shot_prompts + [current_prediction_prompt, image, html_prompt, html_content, response_format_prompt]

        elif self.mode == "ss":
            model_prompt = [zero_shot_prompt] + few_shot_prompts + [current_prediction_prompt, image, response_format_prompt]

        elif self.mode == "html":
            model_prompt = [zero_shot_prompt] + few_shot_prompts + [current_prediction_prompt, html_prompt, html_content, response_format_prompt]
        
        return model_prompt

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
                        if self.mode == "html" or self.mode == "both":
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
    parser.add_argument("mode", help="ss only, html only or both?")
    args = parser.parse_args()

    phishing_folders = utils.phishing_folders_oct + utils.phishing_folders_nov + utils.phishing_folders_dec
    if args.benign_phishing == "benign":
        folders = utils.benign_folders
    else:
        folders = phishing_folders
       
    gemini_baseline = GeminiProVisionBaseline(args.benign_phishing, args.mode)
    for few_shot_count in ["3"]:    
        for folder in folders:
            print(f"\n[{few_shot_count}-shot] Processing folder: {folder}")
            folder_path = os.path.join("baseline", "datasets", f"original_dataset_{folder}")
            date = folder
            gemini_baseline.analyse_directory(folder_path, date, int(few_shot_count))
            time.sleep(random.randint(10, 20))


   