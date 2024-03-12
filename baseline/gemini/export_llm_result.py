import argparse
import openpyxl
from utils.file_utils import FileUtils

class LlmResultExport:
    def __init__(self, file_hash_column, predicted_brand_column, has_credentials_column, has_call_to_action_column, confidence_score_column):
        self.file_hash_column = file_hash_column
        self.predicted_brand_column = predicted_brand_column
        self.has_credentials_column = has_credentials_column
        self.has_call_to_action_column = has_call_to_action_column
        self.confidence_score_column = confidence_score_column

    def update_sheet(self, sheet, file_hash, brand, has_credentials, has_call_to_action, confidence_score):
        print(f"\nProcessing file: {file_hash}...")
        hash_found = False
        # Row 1 has headers
        for row in range(2, sheet.max_row + 1):
            if sheet[self.file_hash_column + str(row)].value == file_hash:
                sheet[self.predicted_brand_column + str(row)] = brand
                sheet[self.has_credentials_column + str(row)] = has_credentials
                sheet[self.has_call_to_action_column + str(row)] = has_call_to_action
                sheet[self.confidence_score_column + str(row)] = confidence_score
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

        self.update_sheet(sheet, file_hash, brand, has_credentials, has_call_to_action, confidence_score)


    def update_sheet_with_responses(self, json_file_path, excel_file_path):
        entries = FileUtils.read_from_json_file(json_file_path)
        wb = openpyxl.load_workbook(excel_file_path)
        sheet = wb.active
        
        for entry in entries:
            self.process_individual_entry(sheet, entry)
        wb.save(excel_file_path)
        

    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    parser.add_argument("json_path", help="Analysis jsonfile path")
    parser.add_argument("sheet_path", help="Excel sheet file path")
    parser.add_argument("hash_col", help="File Hash Column")
    parser.add_argument("brand_col", help="Predicted Brand Column")
    parser.add_argument("credentials", help="Has_credentials Column")
    parser.add_argument("call_to_actions", help="Has_Call_To_Action Column")
    parser.add_argument("confidence_score", help="Confidence Score Column")
    args = parser.parse_args()

    export_object = LlmResultExport(args.hash_col, args.brand_col, args.credentials, args.call_to_actions, args.confidence_score)
    export_object.update_sheet_with_responses(args.json_path, args.sheet_path)
