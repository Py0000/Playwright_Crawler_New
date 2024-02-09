import json
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import numpy as np

"""
LIMITATION: Google API rate limiting !!!
"""

def func(json_data_file):
    with open(json_data_file, 'r') as file:
        json_data = json.load(file)

    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('drive-config.json', scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_key("1TDiqjPnUM-Grfimux-oLNWaFyral7oW8EeNyqrQNDbg").worksheet('comparison-1-week')

    # Extract and print all of the values
    list_of_hashes = sheet.get_all_records()
    df = pd.DataFrame(list_of_hashes)
    df = df.replace([np.inf, -np.inf, np.nan], None)

    for key, values in json_data.items():
        row_index = df.index[df['File Hash'] == key].tolist()
    if row_index:
        # +2 to account for the DataFrame's zero-based index and the fact that the first row is headers
        row_number = row_index[0] + 2
        # Create the new row with the updated values
        new_row = df.iloc[row_index[0]].tolist()
        # Replace inf, -inf, and NaN in the new_row before updating
        new_row = [None if isinstance(x, float) and (np.isnan(x) or np.isinf(x)) else x for x in new_row]
        # Update the row in the sheet
        sheet.update(f'A{row_number}:I{row_number}', [new_row], value_input_option='USER_ENTERED')
    
    new_records = df.values.tolist()
    for i, record in enumerate(new_records, start=2):  # Assuming row 1 is headers
        sheet.update(f'A{i}:I{i}', values=[record])



func("011123_screenshot_hashes.json")