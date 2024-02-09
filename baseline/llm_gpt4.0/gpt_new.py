import argparse
import base64
import json
import os
import time
import shutil
import zipfile
from openai import OpenAI


def get_api_key(key_file):
    with open(key_file, 'r') as file:
        api_key = file.readline().strip()
    
    return api_key


def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def format_response(response):
    formatted_text = response.replace("\n\n1.", "\n1.").replace("\n\n2.", "\n2.").replace("\n\n3.", "\n3.").replace("\n\n4.", "\n4.")
    formatted_text = formatted_text.replace(": \n", ": ")
    return formatted_text

def gpt_analysis(image_path, provided_url, visited_url):
    folder_hash = image_path.split("/")[1]
    api_key = get_api_key("api_key.txt")
    client = OpenAI(api_key=api_key)
    encoded_image = encode_image_to_base64(image_path)

    system_prompt = "You are an expert at analyzing webpage screenshots(images) and webpage urls for phishing webpage detection."
    
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "system",
                "content": [
                    {"type": "text", "text": system_prompt},
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"},
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Provided URL: {provided_url}"},
                ],
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Visited URL: {visited_url}"},
                ],
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "From the provided webpage screenshot and url, you are able to determine whether the webpage under examination is a phishing site or not. As you determine whether the webpage is phishing, do also identify the target brand, any user credential fields, the phishing indicators. Provide your response in the following format: 1. Target Brand, 2. Has user credential fields (i.e Yes/No) 3. (List of) Phishing Indicators, 4. Conclusion (i.e Phishing/Non-phishing)."},
                ],
            },
        ],
        max_tokens=4096,
    )

    # Returns the content of the response received from the GPT model
    return format_response(folder_hash + "\n" + response.choices[0].message.content)

    # Prints information about the usage of the model
    # print(response.usage.model_dump())


def process_directory(zip_folder_path, benign_phishing):
    responses = []

    for zip_file in os.listdir(zip_folder_path):
        print(f"Processing {zip_file}")
        time.sleep(3)
        if zip_file.endswith(".zip"):
            zip_path = os.path.join(zip_folder_path, zip_file)

            # Extract the zip file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                extract_path = os.path.join(zip_folder_path, zip_file.replace('.zip', ''))
                zip_ref.extractall(extract_path)
                if benign_phishing == "phishing":
                    self_ref_path = os.path.join(extract_path, extract_path.split("/")[1], 'self_ref')
                else:
                    self_ref_path = os.path.join(extract_path, 'self_ref')
                
                # Find the screenshot and log file in the extracted folder
                if os.path.exists(self_ref_path):
                    screenshot_path = os.path.join(self_ref_path, 'screenshot_aft.png')
                    log_path = os.path.join(self_ref_path, 'log.json')

                    if not os.path.exists(screenshot_path) or not os.path.exists(log_path):
                        continue

                    # Read URLs from log.json
                    with open(log_path, 'r') as log_file:
                        log_data = json.load(log_file)
                        provided_url = log_data.get("Provided Url", "")
                        visited_url = log_data.get("Url visited", "")

                    gpt_resp = gpt_analysis(screenshot_path, provided_url, visited_url)
                    responses.append(gpt_resp)

                # Delete the extracted folder after processing
                shutil.rmtree(extract_path)
    
    date = zip_folder_path.split("_")[-1]
    output_file = f"gpt_analysis_{date}.txt"
    with open(output_file, 'w') as file:
        for response in responses:
            file.write(response + "\n\n\n")
        
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    parser.add_argument("folder_path", help="Folder name")
    parser.add_argument("benign_phishing", help="benign or phishing")
    args = parser.parse_args()

    folder_name = args.folder_path 
    process_directory(folder_name, args.benign_phishing)