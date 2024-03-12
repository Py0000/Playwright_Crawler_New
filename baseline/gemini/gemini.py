import argparse
import json
import os
import shutil
import zipfile

import google.generativeai as genai

import PIL.Image
from baseline.utils import utils


class GeminiProVisionBaseline:
    def __init__(self, mode):
        self.mode = mode
        self.model = self.setup_model()
        self.standard_prompt = self.generate_prompt()

    def setup_model(self):
        genai.configure(api_key=utils.get_api_key("Baseline/llm_geminipro/api_key.txt"))
        model = genai.GenerativeModel('gemini-pro-vision')
        return model
    
    def generate_prompt(self):
        system_prompt = "You are an expert at analyzing webpage screenshots and urls for phishing webpage detection."
        
        response_format_prompt_title = "From the provided information, you are able to determine whether the webpage is a phishing site or not. As you determine whether the webpage is phishing, do also identify the target brand, any user credential fields, the phishing indicators."
        response_format_prompt_body_0 = "Provide your response in the following format:"
        response_format_prompt_body_1 = "1. Conclusion (Phishing/Non-phishing)."
        response_format_prompt_body_2 = "2. Target Brand: " 
        response_format_prompt_body_3 = "3. Has user credential fields: (Yes/No). If yes what are the fields present (i.e. what are the fields asking for?)"
        response_format_prompt_body_4 = "4. Phishing Indicators: , or Reason why it is not phishing: "
        response_format_prompt_body = f"{response_format_prompt_body_0}\n{response_format_prompt_body_1}\n{response_format_prompt_body_2}\n{response_format_prompt_body_3}\n{response_format_prompt_body_4}"

        prompt = f"{system_prompt}\n\n{response_format_prompt_title}\n\n{response_format_prompt_body}\n\n"
        return prompt


    def analyse_individual_data(self, model, image_path, provided_url, visited_url):
        url_prompt = f"Provided_Url: {provided_url}. Visited_Url: {visited_url}"
        full_prompt = f"{self.standard_prompt}\n\n{url_prompt}"
        try: 
            image = PIL.Image.open(image_path)
            folder_hash = image_path.split("/")[3]

            response = model.generate_content([full_prompt, image], stream=True)
            response.resolve()
            return f"{folder_hash}\n{response.text}"
        except Exception as e:
            print(e)
            return f"{folder_hash}\n{str(e)}"


    def analyse_directory(self, zip_folder_path, date):
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
                    
                    # Find the screenshot and log file in the extracted folder
                    if os.path.exists(self_ref_path):
                        screenshot_path = os.path.join(self_ref_path, 'screenshot_aft.png')
                        log_path = os.path.join(self_ref_path, 'log.json')

                        if not os.path.exists(screenshot_path) or not os.path.exists(log_path):
                            continue
                        
                        # Read URLs from log.json
                        with open(log_path, 'r') as log_file:
                            log_data = json.load(log_file)
                            provided_url = log_data.get("Provided Url", "")
                            visited_url = log_data.get("Url visited", "")

                        response = self.analyse_individual_data(self.model, screenshot_path, provided_url, visited_url)
                        responses.append(response)
                    
                    # Delete the extracted folder after processing
                    shutil.rmtree(extract_path)

        output_file = f"Baseline/llm_geminipro/gemini_analysis_{date}.txt"
        with open(output_file, 'w') as file:
            for response in responses:
                file.write(response + "\n\n\n")
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    parser.add_argument("folder_path", help="Folder name")
    parser.add_argument("date", help="Date")
    parser.add_argument("benign_phishing", help="benign or phishing")
    args = parser.parse_args()

    gemini_baseline = GeminiProVisionBaseline(args.benign_phishing)
    gemini_baseline.analyse_directory(args.folder_path, args.date)



        
