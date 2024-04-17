import argparse
import os
import random
import re
import time
import PIL.Image
import zipfile
import google.generativeai as genai
from tqdm import tqdm

from utils.file_utils import FileUtils
from baseline.gemini.gemini_html_extractor import HtmlExtractor
from baseline.utils import utils


class GeminiModelConfigurator:
    @staticmethod
    def configure_gemini_model(mode):
        genai.configure(api_key=utils.get_api_key("baseline/gemini/api_key_new.txt"))
        if mode in [GeminiProBaseline.MODE_SCREENSHOT, GeminiProBaseline.MODE_BOTH]:
            return genai.GenerativeModel('gemini-pro-vision')
        elif mode == GeminiProBaseline.MODE_HTML:
            return genai.GenerativeModel('gemini-pro')
    
class GeminiPromptGenerator:
    def __init__(self, mode):
        self.mode = mode
        self.shot_example_path = os.path.join("baseline", "gemini", "prompt_examples")

    def load_prompt_example_descriptions(self, desc_file_path):
        with open(desc_file_path, 'r') as file:
            descriptions = file.readlines()
        return [desc.strip() for desc in descriptions]
    
    def generate_zero_shot_prompt(self):
        prompt_file_path = os.path.join("baseline", "gemini", "prompts")
        mode_files = {
            GeminiProBaseline.MODE_BOTH: ("system_prompt_both.txt", "response_format_prompt.txt", "chain_of_thought_prompt.txt"),
            GeminiProBaseline.MODE_SCREENSHOT: ("system_prompt_ss.txt", "response_format_prompt.txt", "chain_of_thought_prompt.txt"),
            GeminiProBaseline.MODE_HTML: ("system_prompt_html.txt", "response_format_prompt_html.txt", "chain_of_thought_prompt_html.txt")
        }

        system_prompt_file, response_format_file, chain_of_thought_file = mode_files.get(self.mode)
        system_prompt = FileUtils.read_from_txt_file(os.path.join(prompt_file_path, system_prompt_file))
        chain_of_thought_prompt = FileUtils.read_from_txt_file(os.path.join(prompt_file_path, chain_of_thought_file))
        response_format_prompt = FileUtils.read_from_txt_file(os.path.join(prompt_file_path, response_format_file))

        return f"{system_prompt}\n\n{chain_of_thought_prompt}", f"\n\n{response_format_prompt}"
    
    def generate_prompt_example_image(self, index):
        image = PIL.Image.open(os.path.join(self.shot_example_path, f"ss_{index}.png"))
        return image

    def generate_prompt_example_html_info(self, index):
        html_info = FileUtils.read_from_txt_file(os.path.join(self.shot_example_path, f"html_{index}.txt"))
        return html_info

    def generate_prompt_example_desc(self, index):
        img_descs = self.load_prompt_example_descriptions(os.path.join(self.shot_example_path, "img_descs.txt"))
        html_descs = self.load_prompt_example_descriptions(os.path.join(self.shot_example_path, "html_descs.txt"))
        desc = FileUtils.read_from_txt_file(os.path.join(self.shot_example_path, f"analysis_{index}.txt"))

        if self.mode == GeminiProBaseline.MODE_BOTH:
            desc += f"{img_descs[index-1]} {html_descs[index-1]}"
        elif self.mode == GeminiProBaseline.MODE_SCREENSHOT:
            desc += img_descs[index-1]
        elif self.mode == GeminiProBaseline.MODE_HTML:
            desc += html_descs[index-1]
        
        full_prompt = f"Below is an example analysis.\n{desc}"
        return full_prompt
    
    def generate_few_shot_prompt(self, few_shot_count):
        few_shot_prompts = []
        for i in range(few_shot_count):
            if self.mode == GeminiProBaseline.MODE_BOTH:
                example_image = self.generate_prompt_example_image(i + 1)
                example_html = self.generate_prompt_example_html_info(i + 1)
                example_prompt = self.generate_prompt_example_desc(i + 1)
                few_shot_prompts + [example_prompt, example_image, f"HTML info: {example_html}"]
            
            elif self.mode == GeminiProBaseline.MODE_SCREENSHOT:
                example_image = self.generate_prompt_example_image(i + 1)
                example_prompt = self.generate_prompt_example_desc(i + 1)
                few_shot_prompts + [example_prompt, example_image]
            
            elif self.mode == GeminiProBaseline.MODE_HTML:
                example_html = self.generate_prompt_example_html_info(i + 1)
                example_prompt = self.generate_prompt_example_desc(i + 1)
                few_shot_prompts + [example_prompt, f"HTML info: {example_html}"]

        return few_shot_prompts

    def generate_full_model_prompt(self, few_shot_count, image, html_content):
        zero_shot_prompt, response_format_prompt = self.generate_zero_shot_prompt()
        few_shot_prompts = self.generate_few_shot_prompt(few_shot_count)
        
        current_prediction_prompt = "Here are the provided resources: "
        model_prompt = [zero_shot_prompt] + few_shot_prompts
        if self.mode == GeminiProBaseline.MODE_BOTH:
            model_prompt += [current_prediction_prompt, image, html_content]
        elif self.mode == GeminiProBaseline.MODE_SCREENSHOT:
            model_prompt += [current_prediction_prompt, image]
        elif self.mode == GeminiProBaseline.MODE_HTML:
            model_prompt += [current_prediction_prompt, html_content]

        model_prompt.append(response_format_prompt)
        return model_prompt

class GeminiResponseParser:
    def __init__(self):
        pass

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

class GeminiProBaseline:

    MODE_SCREENSHOT = "ss"
    MODE_HTML = "html"
    MODE_BOTH = "both"

    def __init__(self, phishing_mode, mode):
        self.phishing_mode = phishing_mode
        self.mode = mode
        self.html_extractor = HtmlExtractor()
        self.prompt_generator = GeminiPromptGenerator(mode)
        self.response_parser = GeminiResponseParser()
        self.model = GeminiModelConfigurator.configure_gemini_model(mode)

    
    def obtain_page_url(self, zip_file):
        log_path = FileUtils.extract_file_path_from_zipped(zip_file, "self_ref", "log.json")
        url = "Not found"
        if log_path:
            with zip_file.open(log_path) as log_file:
                log_data = FileUtils.read_from_json_zipped_file(log_file)
                url = log_data["Url visited"]
        return url

    def analyse_zip_file(self, image, few_shot_count, hash, html_content):
        try: 
            model_prompt = self.prompt_generator.generate_full_model_prompt(few_shot_count, image, html_content)
            response = self.model.generate_content(model_prompt)
            response.resolve()
            data = self.response_parser.format_model_response(hash, response.text, is_error=False)
            return data
        except Exception as e:
            data = self.response_parser.format_model_response(hash, str(e), is_error=True)
            print(e)
            return data

    def process_zip_file(self, zip_path, hash, few_shot_count):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            screenshot_path, html_path = None, None
            image = None
            if self.mode in [self.MODE_BOTH, self.MODE_SCREENSHOT]:
                screenshot_path = self.extract_file_path(zip_ref, 'screenshot_aft.png')
                if not screenshot_path:
                    return None
                image = PIL.Image.open(zip_ref.open(screenshot_path))
            if self.mode in [self.MODE_BOTH, self.MODE_HTML]:
                html_path = self.extract_file_path(zip_ref, 'html_script_aft.html')
            
            if not html_path:
                html_content = None
            else:
                with zip_ref.open(html_path) as html_file:
                    html = html_file.read().decode('utf-8')
                    html_content = self.html_extractor.extract_relevant_info_from_html(html)
            
            response = self.analyse_zip_file(image, few_shot_count, hash, html_content)
            response.update({"Url": self.obtain_page_url(zip_ref)})
            return response

    def analyse_directory(self, zip_folder_path, date, few_shot_count, result_path):
        responses = []

        for zip_file in tqdm(os.listdir(zip_folder_path)):
            if zip_file.endswith(".zip"):
                hash = zip_file.split(".zip")[0]
                zip_path = os.path.join(zip_folder_path, zip_file)
                response = self.process_zip_file(zip_path, hash, few_shot_count)
                responses.append(response)
                time.sleep(random.randint(1, 3))
        
        output_file = os.path.join(result_path, f"{self.mode}_{date}_{few_shot_count}.json")
        FileUtils.save_as_json_output(output_file, responses)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Identify the brand of the webpage. You can specify the type of analysis and the data mode.")
    parser.add_argument("mode", choices=["ss", "html", "both"], default="both", help="Choose the analysis mode.")
    parser.add_argument("type", choices=["benign", "phishing"], default="phishing", help="Choose type of dataset")
    parser.add_argument("folder", help="Input the folder that contains the dataset", required=True)
    parser.add_argument("result_path", help="Input the folder tto store the results", required=True)
    args = parser.parse_args()
    
    mode_types = {
            "both": GeminiProBaseline.MODE_BOTH,
            "ss": GeminiProBaseline.MODE_SCREENSHOT,
            "html": GeminiProBaseline.MODE_HTML
        }

    mode = mode_types.get(args.mode, None)
    folders = utils.phishing_folders_oct + utils.phishing_folders_nov + utils.phishing_folders_dec
    if args.type == "benign":
        folders = utils.benign_folders

    gemini_baseline = GeminiProBaseline(mode)
    for few_shot_count in ["0"]:    
        for folder in tqdm(folders, desc=f"Processing {args.type} folders"):
            print(f"\n[{args.type} {few_shot_count}-shot] Processing folder: {folder}")
            folder_path = os.path.join(args.folder, f"original_dataset_{folder}")
            date = folder
            gemini_baseline.analyse_directory(folder_path, date, int(few_shot_count), args.result_path)
            time.sleep(random.randint(5, 15))
    
    '''
    Example folder path: datasets/validated/
    Example result path: baseline/gemini/gemini_responses/
    '''

