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
    

    def setup_model(self):
        genai.configure(api_key=utils.get_api_key("Baseline/llm_geminipro/api_key.txt"))
        model = genai.GenerativeModel('gemini-pro-vision')
        return model


    def generate_zero_shot_prompt(self):
        system_prompt = """
            You are an expert in analyzing webpage screenshots and URLs for phishing webpage detection.
            A phishing webpage might have suspicious URL patterns, such as misspelled brand names or unfamiliar domains. 
            They often ask for sensitive information like personal information, passwords or credit card numbers. 
            Moreover, they might have a screenshot that mimics a legitimate site. 
            In contrast, a benign webpage has a reputable domain, and the content matches the known legitimate brand's style.
            Make use of the information from the screenshot provided.
        """

        response_format_prompt = """
            For each webpage screenshot and URL provided, determine:
            1. If the webpage is phishing or non-phishing.
            2. Target Brand 
            3. Any user credential fields requested (identifiy them if there is any)
            4. List the indicators that support your conclusion
        """

        return f"{system_prompt}\n\n{response_format_prompt}"
    
    def generate_resonse_format_prompt(self):
        response_format_requirement = """
            1. Prediction (Phishing/Non-Phishing)
            2. Target Brand
            3. Any user credential fields (Yes/No) + list them if any
            4. Reasons that support prediction
        """

        remarks = "Give your responses based on the format given below:"

        return f"{remarks}\n{response_format_requirement}."
    

    def generate_phishing_example(self):
        provided_url = "http://cmdpgcollege.in/Europecontract23ss/approval2023/Fastrucking-eiuehrgy534gh4g7834y5hh8g4gh345g33509/3mail@b.c"
        visited_url = "https://pub-76761043d7714c019b0d5b4a6d6779ff.r2.dev/newcontractsigning2023.html#3mail@b.c"
        url_prompt = f"Provided_Url: {provided_url}. Visited_Url: {visited_url}"

        image = PIL.Image.open(os.path.join("Baseline", "examples", "phishing", "example_ss.png"))
        with open(os.path.join("Baseline", "examples", "phishing", "example_desc.txt"), 'r') as file:
            desc = file.read()
        
        title_prompt = "This is an example of the phishing page, and reasons why it is phishing. You can use this to aid you in making your predictions (phishing/benign) subsequently"
        full_prompt = f"{title_prompt}\n\n{url_prompt}\n\nBelow is an example analysis based on the image.\n{desc}"

        return full_prompt, image
    

    def provide_benign_example(self):
        provided_url = "https://www.netflix.com/login"
        visited_url = "https://www.netflix.com/login"
        url_prompt = f"Provided_Url: {provided_url}. Visited_Url: {visited_url}"

        image = PIL.Image.open(os.path.join("Baseline", "examples", "benign", "example_ss_benign.png"))
        with open(os.path.join("Baseline", "examples", "benign", "example_desc_benign.txt"), 'r') as file:
            desc = file.read()
        
        title_prompt = "This is an example of the non-phishing page, and reasons why it is non-phishing. You can use this to aid you in making your predictions (phishing/benign) subsequently"
        full_prompt = f"{title_prompt}\n\n{url_prompt}\n\nBelow is an example analysis based on the image.\n{desc}"
        
        return full_prompt, image
       

    def analyse_individual_data(self, model, image_path, provided_url, visited_url):
        zero_shot_prompt = self.generate_zero_shot_prompt()
        response_format = self.generate_resonse_format_prompt()
        phishing_example_prompt, phishing_example_image = self.generate_phishing_example()
        current_prediction_prompt = "Here are the urls and image for you to make your predicition:"
        url_prompt = f"Provided_Url: {provided_url}. Visited_Url: {visited_url}"

        try: 
            image = PIL.Image.open(image_path)
            folder_hash = image_path.split("/")[3]
            model_prompt = [zero_shot_prompt, phishing_example_prompt, phishing_example_image, response_format, current_prediction_prompt, url_prompt, image]
            response = model.generate_content(model_prompt, stream=True)
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
