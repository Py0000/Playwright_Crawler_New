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
    def __init__(self, mode, is_url):
        self.mode = mode
        self.is_url = is_url
        self.model = self.setup_model()
    

    def setup_model(self):
        genai.configure(api_key=utils.get_api_key("baseline/llm_geminipro/api_key.txt"))
        model = genai.GenerativeModel('gemini-pro-vision')
        return model

    def read_text_from_file(self, file_path):
        with open(file_path, 'r') as file:
            desc = file.read()
        return desc

    def generate_zero_shot_prompt(self):
        prompt_file_path = os.path.join("baseline", "llm_geminipro", "prompts")
        system_prompt = self.read_text_from_file(os.path.join(prompt_file_path, "system_prompt.txt"))
        chain_of_thought_prompt = self.read_text_from_file(os.path.join(prompt_file_path, "chain_of_thought_prompt.txt"))
        reponse_format_prompt = self.read_text_from_file(os.path.join(prompt_file_path, "response_format_prompt.txt"))

        return f"{system_prompt}\n\n{chain_of_thought_prompt}", f"\n\n{reponse_format_prompt}"
    
    

    def generate_phishing_example(self, index):
        example_file_path = os.path.join("baseline", "examples", "new", "phishing")

        image = PIL.Image.open(os.path.join(example_file_path, f"ss_{index}.png"))
        desc = self.read_text_from_file(os.path.join(example_file_path, f"desc_{index}.txt"))
        
        title_prompt = "\n\nThis is an example of a phishing page. You can use this to aid you in making your predictions subsequently"
        full_prompt = f"{title_prompt}\n\nBelow is an example analysis based on the image.\n{desc}"

        return full_prompt, image
    

    def generate_benign_example(self, index):
        example_file_path = os.path.join("baseline", "examples", "new", "benign")

        image = PIL.Image.open(os.path.join(example_file_path, f"ss_{index}.png"))
        desc = self.read_text_from_file(os.path.join(example_file_path, f"desc_{index}.txt"))
        
        title_prompt = "\n\nThis is an example of a benign page. You can use this to aid you in making your predictions subsequently"
        full_prompt = f"{title_prompt}\n\nBelow is an example analysis based on the image.\n{desc}"
        
        return full_prompt, image
       

    def analyse_individual_data(self, model, image_path, few_shot_count, visited_url):
        zero_shot_prompt, response_format_prompt = self.generate_zero_shot_prompt()
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
            model_prompt = [zero_shot_prompt] + few_shot_prompts + [current_prediction_prompt, image, response_format_prompt]
            
            if visited_url != None:
                url_prompt = f"This is the webpage url for your reference. Url: {visited_url}"
                model_prompt = [zero_shot_prompt] + few_shot_prompts + [current_prediction_prompt, url_prompt, image, response_format_prompt]
            
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
                        visited_url = None

                        if not os.path.exists(screenshot_path):
                            continue
                        
                        if self.is_url: 
                            log_path = os.path.join(self_ref_path, 'log.json')
                            if not os.path.exists(log_path):
                                continue
                            visited_url = self.get_page_url(log_path)

                        response = self.analyse_individual_data(self.model, screenshot_path, few_shot_count, visited_url)
                        responses.append(response)
                    
                    # Delete the extracted folder after processing
                    shutil.rmtree(extract_path)

        output_file = f"baseline/llm_geminipro/gemini_analysis_{date}_{few_shot_count}.txt"
        with open(output_file, 'w') as file:
            for response in responses:
                file.write(response + "\n\n\n")
    


    def get_page_url(self, log_path):
        with open(log_path, 'r') as log_file:
            log_data = json.load(log_file)
            provided_url = log_data.get("Provided Url", "")
            visited_url = log_data.get("Url visited", "")
        
        return visited_url

        

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Supply the folder names")
    #parser.add_argument("folder_path", help="Folder name")
    #parser.add_argument("date", help="Date")
    parser.add_argument("is_url", help="To input url?")
    parser.add_argument("benign_phishing", help="benign or phishing")
    parser.add_argument("few_shot_count", help="number of examples to include")
    args = parser.parse_args()

    #benign_folders = ["benign"]
    #phishing_folders = ["251023", "261023", "271023", "281023", "011123", "041123", "051123", "061123", "161123", "251123", "111223", "151223", "251223"]
    benign_folders = ["benign_subset"]
    phishing_folders = ["111223"]
    if args.benign_phishing == "benign":
        folders = benign_folders
    else:
        folders = phishing_folders
    
    gemini_baseline = GeminiProVisionBaseline(args.benign_phishing, args.is_url)
    for folder in folders:
        print(f"\nProcessing folder: {folder}")
        folder_path = os.path.join("baseline", "datasets", f"original_dataset_{folder}")
        date = folder
        gemini_baseline.analyse_directory(folder_path, date, int(args.few_shot_count))
        time.sleep(random.randint(30, 60))


   