import argparse
import json
import os
import shutil
import zipfile
import time
import random

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
            You are an expert in analyzing webpage screenshots for phishing webpage identification and detection.
            A phishing webpage often ask for sensitive information like personal information, passwords or credit card numbers. 
            Moreover, they might have a design that mimics a legitimate site. 
            In contrast, a benign webpage has a reputable domain, and the content matches the known legitimate brand's style.
            Make use of the information from the screenshot provided.
        """

        response_format_prompt = """
            For each webpage screenshot, determine:
            1. Target Brand 
            2. Any user credential fields requested (identifiy them if there is any)
            3. Whether if the page is phishing or non-phishing
            4. List the indicators that support your conclusion in (3)
        """

        return f"{system_prompt}\n\n{response_format_prompt}"
    
    def generate_resonse_format_prompt(self):
        response_format_requirement = """
            1. Target Brand
            2. Any user credential fields (Yes/No) + list them if any
            3. Prediction (Phishing/Non-Phishing)
            4. Reasons that support prediction
        """

        remarks = "Give your responses based on the format given below:"

        return f"{remarks}\n{response_format_requirement}."
    

    def generate_phishing_example(self, index):
        example_file_path = os.path.join("Baseline", "examples", "phishing")

        image = PIL.Image.open(os.path.join(example_file_path, f"ss_{index}.png"))
        with open(os.path.join(example_file_path, f"desc_{index}.txt"), 'r') as file:
            desc = file.read()
        
        title_prompt = "This is an example of the phishing page, and reasons why it is phishing. You can use this to aid you in making your predictions (phishing/benign) subsequently"
        full_prompt = f"{title_prompt}\n\nBelow is an example analysis based on the image.\n{desc}"

        return full_prompt, image
    

    def generate_benign_example(self, index):
        example_file_path = os.path.join("Baseline", "examples", "benign")

        image = PIL.Image.open(os.path.join(example_file_path, f"ss_{index}.png"))
        with open(os.path.join(example_file_path, f"desc_{index}.txt"), 'r') as file:
            desc = file.read()
        
        title_prompt = "This is an example of the non-phishing page, and reasons why it is non-phishing. You can use this to aid you in making your predictions (phishing/benign) subsequently"
        full_prompt = f"{title_prompt}\n\nBelow is an example analysis based on the image.\n{desc}"
        
        return full_prompt, image
       

    def analyse_individual_data(self, model, image_path, few_shot_count):
        zero_shot_prompt = self.generate_zero_shot_prompt()
        response_format = self.generate_resonse_format_prompt()
        few_shot_prompts = []
        for i in range(few_shot_count):
            phishing_example_prompt, phishing_example_image = self.generate_phishing_example(i + 1)
            benign_example_prompt, benign_example_image = self.generate_benign_example(i + 1)
            few_shot_prompts.append(phishing_example_prompt)
            few_shot_prompts.append(phishing_example_image)
            few_shot_prompts.append(benign_example_prompt)
            few_shot_prompts.append(benign_example_image)


        current_prediction_prompt = "Here is the image for you to make your predicition:"

        try: 
            image = PIL.Image.open(image_path)
            folder_hash = image_path.split("/")[3]
            model_prompt = [zero_shot_prompt] + few_shot_prompts + [response_format, current_prediction_prompt, image]
            response = model.generate_content(model_prompt, stream=True)
            response.resolve()
            return f"{folder_hash}\n{response.text}"
        except Exception as e:
            print(e)
            return f"{folder_hash}\n{str(e)}"


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

        output_file = f"Baseline/llm_geminipro/gemini_analysis_{date}.txt"
        with open(output_file, 'w') as file:
            for response in responses:
                file.write(response + "\n\n\n")
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    #parser.add_argument("folder_path", help="Folder name")
    #parser.add_argument("date", help="Date")
    parser.add_argument("benign_phishing", help="benign or phishing")
    parser.add_argument("few_shot_count", help="number of examples to include")
    args = parser.parse_args()

    benign_folders = ["benign"]
    phishing_folders = ["251023", "261023", "271023", "281023", "011123", "041123", "051123", "061123", "161123", "251123", "111223", "151223", "251223"]

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
        time.sleep(random.randint(60, 120))
