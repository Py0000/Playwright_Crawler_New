import argparse
import openpyxl
import os
import time

from baseline.gemini.gemini_domain_comparison import GeminiDomainComparator, DomainExtractor
from baseline.utils import utils
from utils.file_utils import FileUtils

class LlmResultExport:
    def __init__(self, file_hash_column, predicted_brand_column, has_credentials_column, has_call_to_action_column, confidence_score_column, sld_column, is_phish_column, is_phish_llm_column):
        self.file_hash_column = file_hash_column
        self.predicted_brand_column = predicted_brand_column
        self.has_credentials_column = has_credentials_column
        self.has_call_to_action_column = has_call_to_action_column
        self.confidence_score_column = confidence_score_column
        self.sld_column = sld_column
        self.is_phish_column = is_phish_column
        self.is_phish_llm_column = is_phish_llm_column
        self.domain_extractor = DomainExtractor()


    def update_sheet(self, sheet, file_hash, brand, has_credentials, has_call_to_action, confidence_score, sld, llm_domain_check):
        print(f"\nProcessing file: {file_hash}...")
        hash_found = False
        is_phishing = 0 if brand.lower() == sld.lower() else 1 

        # Row 1 has headers
        for row in range(2, sheet.max_row + 1):
            if sheet[self.file_hash_column + str(row)].value == file_hash:
                sheet[self.predicted_brand_column + str(row)] = brand
                sheet[self.has_credentials_column + str(row)] = has_credentials
                sheet[self.has_call_to_action_column + str(row)] = has_call_to_action
                sheet[self.confidence_score_column + str(row)] = confidence_score
                sheet[self.sld_column + str(row)] = sld
                sheet[self.is_phish_column + str(row)] = is_phishing
                sheet[self.is_phish_llm_column + str(row)] = llm_domain_check
                hash_found = True
                break
        
        if hash_found:
            print(f"{file_hash} added to excel sheet...")
        else:
            print(f"{file_hash} does not exist...")
    
    def process_individual_entry(self, sheet, entry):
        file_hash = entry["Folder Hash"]
        brand = entry["Brand"]
        has_credentials = entry["Has_Credentials"]
        has_call_to_action = entry["Has_Call_To_Actions"]
        confidence_score = entry["Confidence Score"]
        url = entry["Url"]
        second_level_domain = self.domain_extractor.extract_second_level_domain(url)

        """
        gemini_domain_comparator = GeminiDomainComparator()
        llm_domain_check = gemini_domain_comparator.determine_url_brand_match(url, brand)
        """
        self.update_sheet(sheet, file_hash, brand, has_credentials, has_call_to_action, confidence_score, second_level_domain, llm_domain_check="")


    def update_sheet_with_responses(self, json_file_path, excel_file_path):
        entries = FileUtils.read_from_json_file(json_file_path)
        wb = openpyxl.load_workbook(excel_file_path)
        sheet = wb.active
        
        # count = 0
        for entry in entries:
            """
            if count == 60:
                time.sleep(30)
                count = 0
            """
            self.process_individual_entry(sheet, entry)
            # count += 1
        wb.save(excel_file_path)
        


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply arguments required to convert responses to excel sheet")
    parser.add_argument("shot", help="Few shots used", required=True)
    parser.add_argument("mode", choices=["ss", "html", "both"], default="both", help="Choose the analysis mode.")
    parser.add_argument("folder", help="Path to folder that contains Gemini Responses")
    parser.add_argument("sheet_path", help="Excel sheet file path", required=True)
    parser.add_argument("hash_col", default="B", help="File Hash Column")
    parser.add_argument("brand_col", default="F", help="Predicted Brand Column")
    parser.add_argument("credentials", default="G", help="Has_credentials Column")
    parser.add_argument("call_to_actions", default="H", help="Has_Call_To_Action Column")
    parser.add_argument("confidence_score", default="I", help="Confidence Score Column")
    parser.add_argument("sld", default="J", help="Second Level Domain Column")
    parser.add_argument("is_phish", default="K", help="Is Phishing Column")
    parser.add_argument("is_phish_llm", default="L", help="Is Phishing LLM Column")
    args = parser.parse_args()

    folders = utils.phishing_folders_oct + utils.phishing_folders_nov + utils.phishing_folders_dec + utils.benign_folders
    
    for folder in folders:
        # Sample args.folder = baseline/gemini/gemini_responses/prompt_1_html_only/0-shot
        json_file_path = os.path.join(args.folder, f"{args.mode}_{folder}_{args.shot}.json")
        export_object = LlmResultExport(args.hash_col, args.brand_col, args.credentials, args.call_to_actions, args.confidence_score, args.sld, args.is_phish, args.is_phish_llm)
        export_object.update_sheet_with_responses(json_file_path, args.sheet_path)
 
 
 