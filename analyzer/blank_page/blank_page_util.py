import os
import json
from analyzer.utils import file_utils

def log_files_get_dict_key_and_output_file(date, type, base_output_dir):
    TYPE_MAP = {
        "html": "Html Script (After)",
        "ss_aft": "Screenshot (After) result",
        "ss_bef": "Screenshot (After) result",
        "css": "CSS Style/Sheet",
        "js": "Js",  
    }

    output_file_map = {
        "html": os.path.join(base_output_dir, f"{date}_html_blank"),
        "ss_aft": os.path.join(base_output_dir, f"{date}_ss_aft_blank"),
        "ss_bef": os.path.join(base_output_dir, f"{date}_ss_bef_blank"),
        "css": os.path.join(base_output_dir, f"{date}_css_blank"),
        "js": os.path.join(base_output_dir, f"{date}_js_blank"),
    }

    return TYPE_MAP[type], output_file_map[type]


def spilt_log_files_by_type(consolidated_log_file_path, type, date, base_output_dir):
    both = []
    self_ref = []
    no_ref = []

    if not os.path.exists(base_output_dir):
        os.makedirs(base_output_dir)

    dict_key, output_file_name = log_files_get_dict_key_and_output_file(date, type, base_output_dir)

    with open(consolidated_log_file_path, 'r') as file:
        data = json.load(file)
    
    for folder_name, content in data.items():
        if (isinstance(content['self_ref'], dict) and isinstance(content['no_ref'], dict)):
            is_self_ref_blank = False
            is_no_ref_blank = False

            if content['self_ref'].get(dict_key) == "Blank":
                is_self_ref_blank = True
            if content['no_ref'].get(dict_key) == "Blank":
                is_no_ref_blank = True

            if is_self_ref_blank and is_no_ref_blank:
                both.append(folder_name)
            elif is_self_ref_blank:
                self_ref.append(folder_name)
            elif is_no_ref_blank:
                no_ref.append(folder_name)
        
    
    both_output_file = f"{output_file_name}_both.txt"
    self_ref_output_file = f"{output_file_name}_self_ref.txt"
    no_ref_output_file = f"{output_file_name}_no_ref.txt"       

    file_utils.export_output_as_txt_file(both_output_file, both)
    file_utils.export_output_as_txt_file(self_ref_output_file, self_ref)    
    file_utils.export_output_as_txt_file(no_ref_output_file, no_ref)        


def split_log_files(consolidated_log_file_path, date, types, base_output_dir):
    print("\nGenerating more concise log files...")
    
    for type in types:
        print(f"Generating concise log file based on {type}...")
        spilt_log_files_by_type(consolidated_log_file_path, type, date, base_output_dir)