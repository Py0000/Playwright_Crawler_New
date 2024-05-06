
import os
import baseline.baseline_config as Config
import utils.constants as Constants
from utils.file_utils import FileUtils

class PromptGenerator:
    def __init__(self, mode, prompt_version):
        self.prompt_file_path = os.path.join("baseline", "prompts", prompt_version)
        self.mode = mode
        self.prompt_version = prompt_version
    
    def load_prompt_example_descriptions(self, desc_file_path):
        with open(desc_file_path, 'r') as file:
            descriptions = file.readlines()
        return [desc.strip() for desc in descriptions]
    

    def get_prompt_sections(self):
        mode_files = {
            Config.MODE_BOTH: ("system_prompt_both.txt", "response_format_prompt.txt", "chain_of_thought_prompt_both.txt"),
            Config.MODE_SCREENSHOT: ("system_prompt_ss.txt", "response_format_prompt.txt", "chain_of_thought_prompt_ss.txt"),
            Config.MODE_HTML: ("system_prompt_html.txt", "response_format_prompt_html.txt", "chain_of_thought_prompt_html.txt")
        }

        system_prompt_file, response_format_file, chain_of_thought_file = mode_files.get(self.mode)
        system_prompt = FileUtils.read_from_txt_file(os.path.join(self.prompt_file_path, system_prompt_file))
        chain_of_thought_prompt = FileUtils.read_from_txt_file(os.path.join(self.prompt_file_path, chain_of_thought_file))
        response_format_prompt = FileUtils.read_from_txt_file(os.path.join(self.prompt_file_path, response_format_file))
        return system_prompt, chain_of_thought_prompt, response_format_prompt
    
    '''
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

        if self.mode == Config.MODE_BOTH:
            desc += f"{img_descs[index-1]} {html_descs[index-1]}"
        elif self.mode == Config.MODE_SCREENSHOT:
            desc += img_descs[index-1]
        elif self.mode == Config.MODE_HTML:
            desc += html_descs[index-1]
        
        full_prompt = f"Below is an example analysis.\n{desc}"
        return full_prompt

    def generate_few_shot_prompt(self, few_shot_count):
        few_shot_prompts = []
        for i in range(few_shot_count):
            if self.mode == Config.MODE_BOTH:
                example_image = self.generate_prompt_example_image(i + 1)
                example_html = self.generate_prompt_example_html_info(i + 1)
                example_prompt = self.generate_prompt_example_desc(i + 1)
                few_shot_prompts + [example_prompt, example_image, f"HTML info: {example_html}"]
            
            elif self.mode == Config.MODE_SCREENSHOT:
                example_image = self.generate_prompt_example_image(i + 1)
                example_prompt = self.generate_prompt_example_desc(i + 1)
                few_shot_prompts + [example_prompt, example_image]
            
            elif self.mode == Config.MODE_HTML:
                example_html = self.generate_prompt_example_html_info(i + 1)
                example_prompt = self.generate_prompt_example_desc(i + 1)
                few_shot_prompts + [example_prompt, f"HTML info: {example_html}"]

        return few_shot_prompts
    '''

    