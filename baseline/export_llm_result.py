import argparse
import openpyxl
import re

class LlmResultExport:
    def __init__(self, file_hash_column, predicted_brand_column, predicted_verdict_column):
        self.file_hash_column = file_hash_column
        self.predicted_brand_column = predicted_brand_column
        self.predicted_verdict_column = predicted_verdict_column


    def read_llm_responses(self, txt_file_path):
        with open(txt_file_path, 'r') as file:
            content = file.read().strip()
            entries = re.split(r'\n\s*\n', content)
        return entries

    def update_sheet(self, sheet, file_hash, target_brand, conclusion):
        print(f"\nProcessing file: {file_hash}...")
        hash_found = False
        # Row 1 has headers
        for row in range(2, sheet.max_row + 1):
            if sheet[self.file_hash_column + str(row)].value == file_hash:
                sheet[self.predicted_brand_column + str(row)] = target_brand
                sheet[self.predicted_verdict_column + str(row)] = 'No' if 'non-phishing' in conclusion.lower() else 'Yes'
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
            # Encountered error when gemini-pro generates the response
            print(f"[ERROR LOG] Invalid Entry for file: {file_hash}")
            return

        conclusion = re.search(r'Conclusion: (.+)', entry).group(1).strip()
        target_brand = re.search(r'Target Brand: (.+)', entry).group(1).strip()

        self.update_sheet(sheet, file_hash, target_brand, conclusion)


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
    args = parser.parse_args()

    export_object = LlmResultExport(args.hash_col, args.brand_col, args.verdict_col)
    export_object.update_sheet_with_responses(args.txt_path, args.sheet_path)
