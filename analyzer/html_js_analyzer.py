import argparse
import json
import os
from tqdm import tqdm

from analyzer.browser_fingerprinting import BrowserFingerprintAnalyzer
from analyzer.obfuscation import ObfuscationDetector
from utils.file_utils import FileUtils

class HtmlJsAnalyzer:
    def __init__(self):
        self.browser_fp_analyzer = BrowserFingerprintAnalyzer()
        self.obfuscation_detector = ObfuscationDetector()

    def combine_js_content(self, contents):
        scripts_content = '\n'.join(contents['inline scripts'])
        for external_script in contents['external scripts']:
            for script_content in external_script.values():
                scripts_content += '\n' + script_content
        
        return script_content
    
    
    def analyse_js_by_domain_category(self, js_info_folder, fp_result_folder, obf_result_folder):
        for folder in tqdm(os.listdir(js_info_folder)):
            date_folder = os.path.join(js_info_folder, folder)
            current_date_fingerprint_info = os.path.join(fp_result_folder, folder)
            current_date_obfuscation_info = os.path.join(obf_result_folder, folder)
            FileUtils.check_and_create_folder(current_date_fingerprint_info)
            FileUtils.check_and_create_folder(current_date_obfuscation_info)
            
            for json_file in tqdm(os.listdir(date_folder), desc=f"Processing {folder}"):
                hash = json_file.replace(".json", "")
                json_path = os.path.join(date_folder, json_file)
                try:
                    with open(json_path, 'r') as file:
                        data = json.load(file)
                    script_content = self.combine_js_content(data)
                    
                    fp_data = self.browser_fp_analyzer.search_and_combine_fingerprint_info(script_content)
                    fp_output_file = os.path.join(current_date_fingerprint_info, f"{hash}.json")
                    FileUtils.save_as_json_output(fp_output_file, fp_data)

                    obf_data = self.obfuscation_detector.detect_obfuscation(script_content)
                    obf_output_file = os.path.join(current_date_obfuscation_info, f"{hash}.json")
                    FileUtils.save_as_json_output(obf_output_file, obf_data)
                except Exception as e:
                    print(e)
    
    def consolidate_and_export_results(self, fp_result_path, obf_result_path, domain_category):
        fp_consolidated_data = self.browser_fp_analyzer.consolidate_fingerprint_results(fp_result_path)
        self.browser_fp_analyzer.export_consolidated_to_excel(fp_consolidated_data, fp_result_path, domain_category)

        obf_consolidated_data = self.obfuscation_detector.consolidate_obfuscation_results(obf_result_path)
        self.obfuscation_detector.export_consolidated_to_excel(obf_consolidated_data, obf_result_path, domain_category)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Analysis of browser fingerprinting information")
    parser.add_argument("js_info_path", help="Input the folder that contains the javascript information")
    parser.add_argument("fp_result_path", help="Input the folder to store the fingerprint results")
    parser.add_argument("obf_result_path", help="Input the folder to store the obfuscation results")
    parser.add_argument("domain_category", help="Phishing (state the month), Benign (Top 10k), Benign (less popular)?")
    args = parser.parse_args() 

    html_js_analyzer = HtmlJsAnalyzer()
    html_js_analyzer.analyse_js_by_domain_category(args.js_info_path, args.fp_result_path, args.obf_result_path)
    html_js_analyzer.consolidate_and_export_results(args.fp_result_path, args.obf_result_path, args.domain_category)

    '''
    Example js_info_path: analyzer/js_info/no_ref_Oct or analyzer/js_info/self_ref_top10k
    Example fp_result_path: analyzer/fingerprint_info 
    Example obf_result_path: analyzer/obfuscation_info
    Example domain_category: top10k or Oct
    '''



                    


        


