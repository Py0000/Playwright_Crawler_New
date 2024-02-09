from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import time



def upload_single_file_to_gdrive_with_exponential_backoff(file, file_path, drive_service, drive_folder_id, max_retries=5):
    retry = 0
    while retry < max_retries:
        try:
            # Create a request to upload the file
            media = MediaFileUpload(file_path, mimetype='application/zip')
            request = drive_service.files().create(
                media_body=media,
                body={
                    'name': file,
                    'parents': [drive_folder_id]
                }
            )

            # Execute the request
            file = request.execute()
            print(f"Uploaded {file}\n")

            # Remove the file after successful upload
            os.remove(file_path)
        except:
            wait_time = (2 ** retry)
            print(f"Waiting for {wait_time} seconds before retrying...")
            time.sleep(wait_time)
            retry += 1
        

def upload_to_google_drive(folder_path):
    time.sleep(3)
    credentials = Credentials.from_service_account_file(os.path.join(os.getcwd(), "src", 'drive-config.json'))
    drive_service = build('drive', 'v3', credentials=credentials)
    drive_folder_id = "1m2k5S97KoFABPJ6sf9A_sr2D-G96BWQC"
    
    
    print(f"Uploading {folder_path} to drive...")
    if folder_path.endswith('.zip'):
        file_name = os.path.basename(folder_path)
        upload_single_file_to_gdrive_with_exponential_backoff(file_name, folder_path, drive_service, drive_folder_id)
           


def main_upload():
    dest_folder = os.path.join("Phishing", "dataset")
    if not os.path.exists(dest_folder):
        print("Dest Folder not exist")
        pass

    for folder in os.listdir(dest_folder):
        folder_path = os.path.join(dest_folder, folder)
        try:
            upload_to_google_drive(folder_path)
        except Exception as e:
            print(f"[Error] Upload {folder_path} to drive failed. Due to ", e)


if __name__ == '__main__':
    while True:
        time.sleep(420)
        main_upload()
