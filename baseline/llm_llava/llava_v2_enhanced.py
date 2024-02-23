from transformers import LlavaForConditionalGeneration, AutoProcessor
from PIL import Image
import argparse
import json
import os
import shutil
import zipfile

def get_api_key(key_file):
    with open(key_file, 'r') as file:
        api_key = file.readline().strip()
    
    return api_key

def generate_response(model, processor, image_path, provided_url, visited_url):
    # Structuring the prompts
    print("structuring prompts...")
    system_prompt = """
    You are an AI trained to analyze webpage screenshots for phishing. Given a webpage screenshot and its URL, 
    determine whether the webpage is a phishing or non-phishing page, the target brand of the webpage, as well as the reason why you think it is phishing or non-phishing.
    Additionally, identify if there is any fields asking for user-credentials or sensitive information.
    """

    resp_format = """ Give me your response in the format below:\n
    1. Conclusion: (Phishing/Non-Phishing)
    2. Target Brand: 
    3. Has user credential fields: (Yes/No). (List them if yes)
    4. Reasons supporting your conclusion.
    """


    urls = f"Provided URL: {provided_url}\nVisited URL: {visited_url}"
    full_prompt = f"<image>\nUSER:{system_prompt}\n{resp_format}\n{urls}\n\nASSISTANT:\n"
    image = Image.open(image_path)
    folder_hash = image_path.split("/")[2]

    inputs = processor(text=full_prompt, images=image, return_tensors="pt")

    # Generate output
    print("Sending payload...")
    generate_ids = model.generate(**inputs, max_length=5000)
    print("Generating output...")
    output = processor.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    print("Output generated...")
    print(output)
    spilt_output = output.split("ASSISTANT:\n")[-1]
    return f"{folder_hash}\n{spilt_output}"

def load_model_processor():
    # Load the model and tokenizer 
    print("Loading model...")
    api_key = get_api_key(os.path.join("Baseline", "llm_llava", "api_token.txt"))
    model = LlavaForConditionalGeneration.from_pretrained("llava-hf/llava-1.5-7b-hf", token=api_key)
    processor = AutoProcessor.from_pretrained("llava-hf/llava-1.5-7b-hf", token=api_key)
    print("Model loaded...")
    return model, processor


def process_directory(zip_folder_path, benign_phishing):
    responses = []
    model, processor = load_model_processor()

    for zip_file in os.listdir(zip_folder_path):
        print(f"Processing {zip_file}")
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

                if os.path.exists(self_ref_path):
                    print("Obtaining screenshot and urls...")
                    screenshot_path = os.path.join(self_ref_path, 'screenshot_aft.png')
                    log_path = os.path.join(self_ref_path, 'log.json')

                    if not os.path.exists(screenshot_path) or not os.path.exists(log_path):
                        responses.append("Error due to missing file(s).")
                        continue

                    with open(log_path, 'r') as log_file:
                        log_data = json.load(log_file)
                        provided_url = log_data.get("Provided Url", "")
                        visited_url = log_data.get("Url visited", "")
                    
                    resp = generate_response(model, processor, screenshot_path, provided_url, visited_url)
                    responses.append(resp)
                
                # Delete the extracted folder after processing
                shutil.rmtree(extract_path)
                
    date = zip_folder_path.split("_")[-1]
    output_file = f"llava_analysis_{date}.txt"
    with open(output_file, 'w') as file:
        for response in responses:
            file.write(response + "\n\n\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    parser.add_argument("folder_path", help="Folder name")
    parser.add_argument("benign_phishing", help="benign or phishing")
    args = parser.parse_args()

    print("Running script...")
    folder_name = args.folder_path 
    process_directory(folder_name, args.benign_phishing)