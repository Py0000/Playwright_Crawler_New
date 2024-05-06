import argparse
import os
import random
import time
import PIL.Image
import zipfile
import google.generativeai as genai
from tqdm import tqdm

from baseline.html_extractor import HtmlExtractor
from baseline.prompt import PromptGenerator
from baseline.response_parser import LLMResponseParser
import baseline.baseline_config as Config
import utils.constants as Constants
from utils.file_utils import FileUtils

class GeminiModelConfigurator:
    @staticmethod
    def configure_gemini_model(mode):
        genai.configure(api_key=FileUtils.get_api_key("baseline/gemini/api_key_new.txt"))
        if mode in [Config.MODE_SCREENSHOT, Config.MODE_BOTH]:
            return genai.GenerativeModel('gemini-pro-vision')
        elif mode == Config.MODE_HTML:
            return genai.GenerativeModel('gemini-pro')

class GeminiVerifier:
    def __init__(self):
        self.model = GeminiModelConfigurator.configure_gemini_model(Config.MODE_HTML)


    def verify_input_given(self, input_content):
        verification_prompt = f"Below is the input I am going to give you:\n{input_content}.\nTell me what have you received? Return it as what i have given you, you can ignore brackets/braces."
        response = self.model.generate_content(verification_prompt)
        response.resolve()

        return response.text
    
    def generate_verification_report(self, hash, html_content):
        output_file_path = os.path.join('baseline', 'gemini', 'responses', f'prompt_verification_{hash}.txt')
        html_received = self.verify_input_given(html_content)

        with open(output_file_path, 'w') as f:
            f.write('HTML Info Received:\n')
            f.write(html_received)



class GeminiProBaseline:
    def __init__(self, mode, prompt_version):
        self.mode = mode
        self.html_extractor = HtmlExtractor()
        self.prompt_generator = PromptGenerator(mode, prompt_version)
        self.response_parser = LLMResponseParser()
        self.model = GeminiModelConfigurator.configure_gemini_model(mode)

    
    def obtain_page_url(self, zip_file):
        log_path = FileUtils.extract_file_path_from_zipped(zip_file, "self_ref", "log.json")
        url = "Not found"
        if log_path:
            with zip_file.open(log_path) as log_file:
                log_data = FileUtils.read_from_json_zipped_file(log_file)
                url = log_data["Url visited"]
        return url

    def generate_full_model_prompt(self, few_shot_count, image, html_content):
        system_prompt, chain_of_thought_prompt, response_format_prompt = self.prompt_generator.get_prompt_sections()
        #few_shot_prompts = self.generate_few_shot_prompt(few_shot_count)
        
        current_prediction_prompt = "Here are the provided resources: "
        #model_prompt = [f"{system_prompt}\n\n{chain_of_thought_prompt}"] + few_shot_prompts
        model_prompt = [f"{system_prompt}\n\n{chain_of_thought_prompt}"]
        if self.mode == Config.MODE_BOTH:
            model_prompt += [current_prediction_prompt, image, html_content]
        elif self.mode == Config.MODE_SCREENSHOT:
            model_prompt += [current_prediction_prompt, image]
        elif self.mode == Config.MODE_HTML:
            model_prompt += [current_prediction_prompt, html_content]

        model_prompt.append(f"\n\n{response_format_prompt}")
        return model_prompt 

    
    def analyse_zip_file(self, image, few_shot_count, hash, html_content):
        """ 
        ## Uncomment if needed
        # Checks if model receive input
        verify = GeminiVerifier()
        verify.generate_verification_report(hash, html_content, self.mode)
        """
        try:
            model_prompt = self.generate_full_model_prompt(few_shot_count, image, html_content)
            response = self.model.generate_content(model_prompt)
            response.resolve()
            if not response.parts:
                data = self.response_parser.format_model_response(hash, str(response.candidates), is_error=True)
            else:
                data = self.response_parser.format_model_response(hash, response.text, is_error=False)
            return data
        except Exception as e:
            print(response.prompt_feedback)
            data = self.response_parser.format_model_response(hash, str(e), is_error=True)
            print(e)
            return data

    def process_zip_file(self, zip_path, hash, few_shot_count):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            screenshot_path, html_path = None, None
            image = None
            if self.mode in [Config.MODE_BOTH, Config.MODE_SCREENSHOT]:
                screenshot_path = FileUtils.extract_file_path_from_zipped(zip_ref, 'self_ref', 'screenshot_aft.png')
                if not screenshot_path:
                    return None
                image = PIL.Image.open(zip_ref.open(screenshot_path))
            if self.mode in [Config.MODE_BOTH, Config.MODE_HTML]:
                html_path = FileUtils.extract_file_path_from_zipped(zip_ref, 'self_ref', 'html_script_aft.html')
            
            if not html_path:
                html_content = None
            else:
                with zip_ref.open(html_path) as html_file:
                    html = html_file.read().decode('utf-8')
                    html_content = self.html_extractor.extract_relevant_info_from_html_to_string(html)
            
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
    
    gemini_baseline = GeminiProBaseline(mode, args.prompt_version)
    for few_shot_count in ["0"]:  
        for folder in folders:    
            print(f"[{mode}] Processing {folder}")
            folder_path = os.path.join(args.folder, f"original_dataset_{folder}")
            date = folder
            #folder_path = args.folder # Delete this afterwards  
            #date = 'input_check' # Delete this afterwards  
            gemini_baseline.analyse_directory(folder_path, date, int(few_shot_count), args.result_path)
            time.sleep(random.randint(10, 20))
    
    '''
    Example folder path: datasets/validated/
    Example result path: baseline/gemini/gemini_responses/
    '''

