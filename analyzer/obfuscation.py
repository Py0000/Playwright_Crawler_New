import argparse
import json
import re
from math import log2 
from collections import Counter 
from tqdm import tqdm
import os
import pandas as pd

from utils.file_utils import FileUtils

class ObfuscationDetector:
    def __init__(self):
        pass

    def calculate_entropy(self, text):
        p, lns = Counter(text), float(len(text))
        entropy = -sum(count/lns * log2(count/lns) for count in p.values())

        return entropy
    
    def detect_dynamic_code_execution(self, text):
        eval_pattern = re.compile(r'\beval\s*\(')
        eval_usage = len(eval_pattern.findall(text))
        other_function = len(re.findall(r'\b(new\s+Function\(|setTimeout\(|setInterval\(|execScript\()', text))
        return eval_usage + other_function
    
    def detect_window_doc_usage(self, text):
        return len(re.findall(r'\b(window|document)\[\s*["\']\w+["\']\s*\]', text))

    def determine_func_complexity(self, text):
        return len(re.findall(r'\bfunction\s*\(.*\)\s*{(?:[^{}]*){(?:[^{}]*){', text))
    
    def detect_simple_encrypt_code(self, text):
        encryption_detection_patterns = [
            r'(decrypt|decode)[A-Za-z]*\(',
            r'atob\(',
            r'CryptoJS\.',
        ]

        return sum(len(re.findall(pattern, text)) for pattern in encryption_detection_patterns)

    def detect_identifier_obfuscation(self, text):
        """Detects identifier obfuscation by looking for meaningless variable names."""
        # Example: excessively short or long variable names, or names with unusual patterns
        suspicious_identifiers = re.findall(r'\b[a-z]{1,2}\b|\b[a-z0-9_]{20,}\b', text, re.I)
        return len(suspicious_identifiers)
    
    def detect_string_obfuscation(text):
        """Detects string obfuscation through concatenated and encoded strings"""
        # split_strings = len(re.findall(r"'.*'\s*\+\s*'.*'|\".*\"\s*\+\s*\".*\"", text))
        # Check for long hex-encoded or base64-encoded strings (i.e atleast 20 characters long)
        split_strings = len(re.findall(r'(["\'])(?:\\x[0-9a-fA-F]{2}|\\u[0-9a-fA-F]{4}|[A-Za-z0-9+/=]{20,})\1', text))
        return split_strings
    
    def detect_no_alpha_numeric(text):
        """Detects obfuscated code segments without any alphanumeric characters."""
        # Search for long segments of code with no alphanumeric characters
        non_alphanumeric_segments = re.findall(r'[^a-zA-Z0-9\s]{20,}', text)
        return len(non_alphanumeric_segments)

    def detect_dead_code_injection(self, text):
        """Detects dead code injection."""
        # Simplistic heuristic: looking for functions or loops that do not have any effect
        dead_code_patterns = len(re.findall(r'function\s+[a-zA-Z0-9_]+\(\)\s*\{\s*\}', text)) # empty functions
        dead_code_patterns += len(re.findall(r'for\s*\(;;\)\s*\{\s*\}', text)) # infinite loops
        dead_code_patterns += len(re.findall(r'if\s*\(\s*!\s*!\s*[\w]+\s*\)\s*{', text)) # unusual conditions
        return dead_code_patterns 
    
    def detect_minification_simple(self, text):
        """Detects simple minification techniques."""
        # Simple heuristic based on lack of whitespace and short variable names
        if not re.search(r'\s', text) and re.search(r'\b[a-z]{1,2}\b', text):
            return True
        return False
    
    def detect_obfuscation(self, html_content):
        script_entropy = self.calculate_entropy(html_content)
        has_strings_obfuscation = self.detect_string_obfuscation(html_content)
        has_dynamic_code = self.detect_dynamic_code_execution(html_content)
        has_win_doc_use = self.detect_window_doc_usage(html_content)
        has_complex_func = self.determine_func_complexity(html_content)
        has_encrypted_code = self.detect_simple_encrypt_code(html_content)
        has_dead_code = self.detect_dead_code_injection(html_content)
        non_alnum_seg = self.detect_no_alpha_numeric(html_content)
        simple_minification = self.detect_minification_simple(html_content)
    
        data = {
            "entropy": script_entropy,
            "string_obfuscation": has_strings_obfuscation,
            "Dynamic code": has_dynamic_code,
            "Has Window/Document Usage": has_win_doc_use,
            "Has Complex Functions": has_complex_func,
            "Encrypted Code": has_encrypted_code,
            "Dead Code": has_dead_code,
            "No alphanumeric segments": non_alnum_seg,
            "Simple Minification": simple_minification,
        }

        return data 
    
    def consolidate_obfuscation_results(self, obf_result_folder):
        data = []
        for folder in tqdm(os.listdir(obf_result_folder), desc=f"Consolidating obfuscation for {folder}"):
            folder_path = os.path.join(obf_result_folder, folder)
            if os.path.isdir(folder_path):
                for file in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file)
                    with open(file_path, 'r') as json_file:
                        file_data = json.load(json_file)
                    
                    current_data = {
                        'Date': folder,
                        'File Hash': file.replace(".json", ""),
                        **file_data
                    }
                    data.append(current_data)
        
        return data
        


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Analysis of browser fingerprinting information")
    parser.add_argument("js_info_path", help="Input the folder that contains the javascript information")
    parser.add_argument("result_path", help="Input the folder to store the obfuscation results")
    parser.add_argument("domain_category", help="Phishing (state the month), Benign (Top 10k), Benign (less popular)?")
    args = parser.parse_args() 

    FileUtils.check_and_create_folder(args.result_path)

    obfuscation_detector = ObfuscationDetector()
    obfuscation_detector.analyse_js_by_domain_category(args.js_info_path, args.result_path)
    consolidated_data = obfuscation_detector.consolidate_obfuscation_results(args.result_folder)
    output_file_name = f"obfuscation_summary_{args.domain_category}.xlsx"
    header = ["Date", "File Hash", "Final Verdict", "Entropy", "String Obfuscation", "Has Win/Doc Usage", "Has complex func", "Has encrypted code", "Dead Code", "No alnum segments", "Simple minification", "Advance minification"]
    obfuscation_detector.export_consolidated_to_excel(consolidated_data, args.result_path, output_file_name, header)

    '''
    Example js_info_path: analyzer/js_info
    Example result_path: analyzer/obfuscation_info
    '''


    
