import argparse
import openpyxl
import pandas as pd
import os

class GeminiResultPostProcessor:
    def __init__(self):
        self.max_row_num = 1633
        self.gemini_identified_brand_col = 'F'
        self.is_phishing_col = 'K'
        self.date_col = "A"
        self.brand_same_col = "L"
        self.target_brand_col = "D"
        self.final_verdict_col = "E"
        pass

    def rectify_error_entry(self, worksheet, brand_cell, is_phishing_cell):
        print("Rectifying error pages...")
        if (worksheet[brand_cell].value == "Error Occurred"):
            worksheet[is_phishing_cell].value = "Error Occurred"
        else:
            pass
    
    def check_for_benign_phishing_status(self, worksheet, date_cell, is_brand_same_cell, is_phishing_cell):
        print("Checking benign pages...")
        if worksheet[date_cell].value == "Benign":
            if worksheet[is_brand_same_cell].value == "Yes":
                worksheet[is_phishing_cell] = "No"
            if worksheet[is_brand_same_cell].value == "Indeterminate":
                worksheet[is_phishing_cell] = "Indeterminate"

    def check_for_phishing_phishing_status(self, worksheet, date_cell, is_brand_same_cell, is_phishing_cell, final_verdict_cell):
        print("Checking phishing pages...")
        if worksheet[date_cell].value != "Benign":
            if worksheet[is_brand_same_cell].value == "Yes" and worksheet[final_verdict_cell].value == "No":
                worksheet[is_phishing_cell] = "No"
            if worksheet[is_brand_same_cell].value == "Indeterminate":
                worksheet[is_phishing_cell] = "Indeterminate"

    def main(self, excel_path):
        workbook = openpyxl.load_workbook(excel_path, data_only=True)
        worksheet = workbook.active

        for row in range(2, self.max_row_num + 1):
            gemini_identified_brand_cell = self.gemini_identified_brand_col + str(row)
            is_phishing_cell = self.is_phishing_col + str(row)
            date_cell = self.date_col + str(row)
            is_brand_same_cell = self.brand_same_col + str(row)
            final_verdict_cell = self.final_verdict_col + str(row)
            

            # Check if the 'Gemini Identified Brand' cell contains 'Error Occurred'
            self.rectify_error_entry(worksheet, gemini_identified_brand_cell, is_phishing_cell)

            # Check the phishing status of benign pages. If brand and domain matches, then it is not phishing.
            self.check_for_benign_phishing_status(worksheet, date_cell, is_brand_same_cell, is_phishing_cell)

            # Check the phishing status of benign pages. If brand and domain matches, then it is not phishing.
            self.check_for_phishing_phishing_status(worksheet, date_cell, is_brand_same_cell, is_phishing_cell, final_verdict_cell)

        workbook.save(excel_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    parser.add_argument("excel_path", help="excel sheet path")
    args = parser.parse_args()

    post_processor = GeminiResultPostProcessor()
    post_processor.main(args.excel_path)