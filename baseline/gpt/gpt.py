import argparse
import base64
import json
import os
import random
import time

from tqdm import tqdm

from openai import OpenAI

from baseline.prompt import PromptGenerator
from baseline.response_parser import LLMResponseParser
import baseline.baseline_config as Config
from utils.file_utils import FileUtils
import utils.constants as Constants

class GPT4Verifier:
    def __init__(self):
        self.model = "gpt-4-turbo-2024-04-09"
        self.client = OpenAI(api_key=FileUtils.get_api_key(os.path.join('baseline', 'gpt', 'api_key.txt')))
    
    def verify_input_given(self, input_content):
        verification_prompt = f"Below is the input I am going to give you.\nTell me what have you received? Return it as what i have given you, you can ignore brackets/braces."
        input_prompt = f"Here is the input:\n{input_content}"
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": [
                        {"type": "text", "text": verification_prompt},
                    ],
                },
                {
                    "role": "system",
                    "content": [
                        {"type": "text", "text": input_prompt},
                    ],
                },
            ],
            max_tokens=4096,
        )
        return response.choices[0].message.content
    
    def generate_verification_report(self, hash, html_content):
        output_file_path = os.path.join('baseline', 'gpt', 'responses', f'prompt_verification_{hash}.txt')
        html_received = self.verify_input_given(html_content)

        with open(output_file_path, 'w') as f:
            f.write('HTML Info Received:\n')
            f.write(html_received)

class GPT4Baseline:
    def __init__(self, mode, prompt_version):
        self.mode = mode
        self.prompt_generator = PromptGenerator(mode, prompt_version)
        self.response_parser = LLMResponseParser()
        self.model = "gpt-4-turbo-2024-04-09"
        self.client = OpenAI(api_key=FileUtils.get_api_key(os.path.join('baseline', 'gpt', 'api_key.txt')))
    
    def encode_image_to_base64(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    
    def generate_full_model_prompt(self, few_shot_count, encoded_image, html_content):
        system_prompt, chain_of_thought_prompt, response_format_prompt = self.prompt_generator.get_prompt_sections()
        
        system_message = {
            "role": "system",
            "content": [
                {"type": "text", "text": f"{system_prompt}\n\n{chain_of_thought_prompt}"},
            ],
        }

        response_format_message = {
            "role": "user",
            "content": [
                {"type": "text", "text": response_format_prompt},
            ],
        }

        image_message = {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"},
                }
            ],
        }

        html_content_message = {
            "role": "user",
            "content": [
                {"type": "text", "text": f"Here is the html information: {html_content}"},
            ],
        }

        if self.mode == Config.MODE_BOTH:
            messages = [system_message, image_message, html_content_message, response_format_message]
        elif self.mode == Config.MODE_SCREENSHOT:
            messages = [system_message, image_message, response_format_message]
        elif self.mode == Config.MODE_HTML:
            messages = [system_message, html_content_message, response_format_message]
        
        return messages
        
    

    def analyse_zip_file(self, encoded_image, few_shot_count, hash, html_content):
        '''
        ## Uncomment if needed
        # Checks if model receive input
        verify = GPT4Verifier()
        verify.generate_verification_report(hash, html_content)
        '''
        
        try: 
            messages = self.generate_full_model_prompt(few_shot_count, encoded_image, html_content)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=4096,
            )

            generated_response = response.choices[0].message.content
            data = self.response_parser.format_model_response(hash, generated_response, is_error=False)
            return data
        except Exception as e:
            data = self.response_parser.format_model_response(hash, str(e), is_error=True)
            print(e)
            return data



    def process_zip_file(self, folder_path, hash, few_shot_count):
        screenshot_path, add_info_path = None, None
        encoded_image, html_content, url = None, None, None
        if self.mode in [Config.MODE_BOTH, Config.MODE_SCREENSHOT]:
            screenshot_path = os.path.join(folder_path, 'screenshot_aft.png')
            if not os.path.exists(screenshot_path):
                return None
            encoded_image = self.encode_image_to_base64(screenshot_path)

        add_info_path = os.path.join(folder_path, 'add_info.json')
        if os.path.exists(add_info_path):
            add_info = FileUtils.read_from_json_file(add_info_path)
            if self.mode in [Config.MODE_BOTH, Config.MODE_HTML]:
                html_content = add_info['html_brand_info']
            url = add_info['Url']
        
        response = self.analyse_zip_file(encoded_image, few_shot_count, hash, html_content)
        response.update({"Url": url})
        return response


    def analyse_directory(self, dataset_folder_path, date, few_shot_count, result_path):
        responses = []
        
        for folder in tqdm(os.listdir(dataset_folder_path)):
            hash = folder
            folder_path = os.path.join(dataset_folder_path, folder)
            response = self.process_zip_file(folder_path, hash, few_shot_count)
            responses.append(response)
            time.sleep(random.randint(1, 3))
        
        output_file = os.path.join(result_path, f"{self.mode}_{date}_{few_shot_count}.json")
        FileUtils.save_as_json_output(output_file, responses)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Identify the brand of the webpage. You can specify the type of analysis and the data mode.")
    parser.add_argument("mode", choices=["ss", "html", "both"], default="both", help="Choose the analysis mode.")
    parser.add_argument("phishing_mode", choices=["phishing", "benign"], default="phishing", help="Choose the dataset type.")
    parser.add_argument("folder", help="Input the folder that contains the dataset")
    parser.add_argument("result_path", help="Input the folder to store the results")
    parser.add_argument("prompt_version", default="original", help="Which prompt to use")
    args = parser.parse_args()

    if not os.path.exists(args.result_path):
        os.makedirs(args.result_path)
    
    mode_types = {
            "both": Config.MODE_BOTH,
            "ss": Config.MODE_SCREENSHOT,
            "html": Config.MODE_HTML
        }

    mode = mode_types.get(args.mode, None)
    folders = Constants.PHISHING_FOLDERS_VALIDATED_OCT + Constants.PHISHING_FOLDERS_VALIDATED_NOV + Constants.PHISHING_FOLDERS_VALIDATED_DEC
    if args.phishing_mode == "benign":
        folders = Constants.BENIGN_FOLDERS_VALIDATED

    gpt_baseline = GPT4Baseline(mode, args.prompt_version)
    for few_shot_count in ["0"]:
        for folder in folders:
            print(f"[{mode}] Processing {folder}")
            folder_path = os.path.join(args.folder, f"{folder}")
            date = folder
            gpt_baseline.analyse_directory(folder_path, date, int(few_shot_count), args.result_path)
            time.sleep(random.randint(5, 15))
    
    '''
    Example folder path: datasets/llm/
    Example result path: baseline/gpt/responses/
    '''