import argparse
import openpyxl
import re

class LlmResultExport:
    def __init__(self, file_hash_column, predicted_brand_column, predicted_verdict_column, has_credentials_column, phishing_score_column):
        self.file_hash_column = file_hash_column
        self.predicted_brand_column = predicted_brand_column
        self.predicted_verdict_column = predicted_verdict_column
        self.has_credentials_column = has_credentials_column
        self.phishing_score_column = phishing_score_column


    def read_llm_responses(self, txt_file_path):
        with open(txt_file_path, 'r') as file:
            content = file.read().strip()
            entries = re.split(r'\n\s*\n', content)
        return entries

    def update_sheet(self, sheet, file_hash, target_brand, conclusion, has_credentials, phishing_score):
        print(f"\nProcessing file: {file_hash}...")
        hash_found = False
        # Row 1 has headers
        for row in range(2, sheet.max_row + 1):
            if sheet[self.file_hash_column + str(row)].value == file_hash:
                sheet[self.predicted_brand_column + str(row)] = target_brand
                sheet[self.predicted_verdict_column + str(row)] = 'Yes' if 'phishing' in conclusion.lower() else 'No'
                sheet[self.has_credentials_column + str(row)] = has_credentials
                sheet[self.phishing_score_column + str(row)] = phishing_score
                hash_found = True
                break
        
        if hash_found:
            print(f"{file_hash} added to excel sheet...")
        else:
            print(f"{file_hash} does not exist...")
    
    def process_individual_entry(self, sheet, entry):
        lines = [line for line in entry.split('\n') if line.strip() != '']
        file_hash = lines[0].strip()

        if len(lines) <= 2:
            isExceeded = re.search(r'400 Request payload size exceeds the limit: (.+)', entry).group(1).strip()
            if isExceeded:
                conclusion = "Payload exceeds limit"
                target_brand = "Payload exceeds limit"
                has_credentials = "Payload exceeds limit"
                phishing_score = "Payload exceeds limit"

            # Encountered error when gemini-pro generates the response
            print(f"[ERROR LOG] Invalid Entry for file: {file_hash}")
            return

        conclusion = re.search(r'Conclusion: (.+)', entry).group(1).strip()
        target_brand = re.search(r'Target brand: (.+)', entry).group(1).strip()
        has_credentials = re.search(r'Has credentials/call-to-action: (.+)', entry).group(1).strip()
        phishing_score = re.search(r'Phishing Score: (.+)', entry).group(1).strip()

        if target_brand.lower() == "na" or target_brand.lower == "n/a":
            target_brand = "Indeterminate"

        self.update_sheet(sheet, file_hash, target_brand, conclusion, has_credentials, phishing_score)


    def update_sheet_with_responses(self, txt_file_path, excel_file_path):
        entries = self.read_llm_responses(txt_file_path)
        wb = openpyxl.load_workbook(excel_file_path)
        sheet = wb.active
        
        for entry in entries:
            self.process_individual_entry(sheet, entry)
        wb.save(excel_file_path)
        

    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    parser.add_argument("txt_path", help="Analysis txt file path")
    parser.add_argument("sheet_path", help="Excel sheet file path")
    parser.add_argument("hash_col", help="File Hash Column")
    parser.add_argument("brand_col", help="Predicted Brand Column")
    parser.add_argument("verdict_col", help="Predicted Verdict Column")
    parser.add_argument("credentials", help="Has_credentials Column")
    parser.add_argument("phishing_score", help="Phishing Score Column")
    args = parser.parse_args()

    export_object = LlmResultExport(args.hash_col, args.brand_col, args.verdict_col, args.credentials, args.phishing_score)
    export_object.update_sheet_with_responses(args.txt_path, args.sheet_path)
