import hashlib
import io
import json 
import os
import shutil 
from PIL import Image
import numpy as np
from tqdm import tqdm
from filter.blank_image_analysis import BlankScreenshotDetector
import imagehash
import signal

'''
Used to filter out blank, error and duplicated images from dataset crawled for training VisualPhishNet
'''
timeout_duration = 15  
def handler(signum, frame):
    raise TimeoutError("Timed out!")

def remove_duplicates(json_file_path):
    target_folder = os.path.join('datasets', 'vpn_others', 'dup')
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    with open(json_file_path, 'r') as file:
        duplicates = json.load(file)
    
    for _, files in duplicates.items():
        # Skip the first file (consider it the original) and delete the rest
        for file_path in files[1:]:  # This starts from the second item
            try:
                target_path = os.path.join(target_folder, file_path)
                shutil.move(file_path, target_path)
                print(f"Removed: {file_path}")
            except FileNotFoundError:
                print(f"File not found, could not remove: {file_path}")
            except Exception as e:
                print(f"Error removing {file_path}: {e}")





dataset_path = os.path.join('datasets', 'vpn')



blank_detector = BlankScreenshotDetector()
'''
for brand_folder in os.listdir(dataset_path):
    print(brand_folder)
    blanks = {}
    brand_folder_path = os.path.join(dataset_path, brand_folder)
    if not os.path.isdir(brand_folder_path):
        continue
    
    count = 0
    for sample_folder in tqdm(os.listdir(brand_folder_path)):
        sample_folder_path = os.path.join(brand_folder_path, sample_folder)
        log_path = os.path.join(brand_folder_path, sample_folder, 'self_ref', 'log.json')
        target_folder = os.path.join('datasets', 'vpn_others', 'errors')
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        target_path = os.path.join(target_folder, f"{brand_folder}_{sample_folder}")

        if not os.path.exists(log_path): 
            shutil.move(sample_folder_path, target_path)
            print("does not exist", sample_folder)
            continue
        else:
            # Set up a timeout for the processing
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(timeout_duration)  # Set the alarm

            with open(log_path, 'r') as json_file:
                try:
                    data = json.load(json_file)
                except:
                    print(f"Error decoding JSON in {log_path}. Moving {sample_folder} to errors.")
                    shutil.move(sample_folder_path, target_path)

            ss_exist = data["Client-side screenshot obtained?"] == "Success"
            html_exist = data["Client-Side HTML script obtained?"] == "Success"
            collect_success = data["Status"] == 200

            if not collect_success or not ss_exist or not html_exist:
                shutil.move(sample_folder_path, target_path)
                print("errorneous", sample_folder)
                continue

            # Reset the alarm
            signal.alarm(0)
'''

for brand_folder in os.listdir(dataset_path):
    print(brand_folder)
    brand_folder_path = os.path.join(dataset_path, brand_folder)
    if not os.path.isdir(brand_folder_path):
        continue
    
    for sample_folder in tqdm(os.listdir(brand_folder_path)):
        try:
            sample_folder_path = os.path.join(brand_folder_path, sample_folder)
            # Set up a timeout for the processing
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(timeout_duration)  # Set the alarm

            image_path = os.path.join(brand_folder_path, sample_folder, 'self_ref', 'screenshot_aft.png')
            try:
                with open(image_path, 'rb') as image_file:
                    image = Image.open(io.BytesIO(image_file.read()))
                    gray_image = np.array(image.convert('L')) # Convert image to grey-scale
                    sd = blank_detector.get_standard_deviation_of_grayscaled_ss(gray_image)
                    ce = blank_detector.get_canny_edge_count_of_grayscaled_ss(gray_image)
                    tc = blank_detector.get_length_of_text_in_ss(gray_image)

                    is_potential_blank = blank_detector.is_potential_blank_ss(sd, ce, tc)
                    if is_potential_blank:
                        target_folder = os.path.join('datasets', 'vpn_others', 'blank')
                        if not os.path.exists(target_folder):
                            os.makedirs(target_folder)
                        target_path = os.path.join(target_folder, f"{brand_folder}_{sample_folder}")
                        shutil.move(sample_folder_path, target_path)
                        print("blank removed", sample_folder)
            except Exception as e:
                target_folder = os.path.join('datasets', 'vpn_others', 'blank_error')
                if not os.path.exists(target_folder):
                    os.makedirs(target_folder)
                target_path = os.path.join(target_folder, f"{brand_folder}_{sample_folder}")
                print("Analysis error for: ", sample_folder)
                shutil.move(sample_folder_path, target_path)
                continue


            # Reset the alarm
            signal.alarm(0)

        except TimeoutError:
            # Handle timeout
            target_folder = os.path.join('datasets', 'vpn_others', 'blank_timedout')
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)
            target_path = os.path.join(target_folder, f"{brand_folder}_{sample_folder}")
            print("Timeout occurred for", sample_folder)
            shutil.move(sample_folder_path, target_path)
            continue
    


for brand_folder in os.listdir(dataset_path):
    duplicates = {}

    brand_folder_path = os.path.join(dataset_path, brand_folder)
    if not os.path.isdir(brand_folder_path):
        continue

    for sample_folder in tqdm(os.listdir(brand_folder_path)):
        sample_folder_path = os.path.join(brand_folder_path, sample_folder)
        image_path = os.path.join(brand_folder_path, sample_folder, 'self_ref', 'screenshot_aft.png')
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
            # get image hash
            hash_func = hashlib.sha256()
            hash_func.update(image_data)
            img_hash = hash_func.hexdigest()
        
        # Check for duplicates by exact hash and add to dictionary
        if img_hash in duplicates:
            duplicates[img_hash].append(sample_folder_path)
        else:
            duplicates[img_hash] = [sample_folder_path]
        
            
    
    result = {key: val for key, val in duplicates.items() if len(val) > 1}
    if result:
        print(f"{brand_folder} Has duplicates")
        with open(f"{brand_folder}_dup.json", 'w') as json_file:
            json.dump(result, json_file, indent=4)
        
        remove_duplicates(f"{brand_folder}_dup.json")
    else:
        print(f"{brand_folder} No duplicates")

for brand_folder in os.listdir(dataset_path):
    duplicates = {}
    hashes = {}

    brand_folder_path = os.path.join(dataset_path, brand_folder)
    if not os.path.isdir(brand_folder_path):
        continue

    for sample_folder in tqdm(os.listdir(brand_folder_path)):
        sample_folder_path = os.path.join(brand_folder_path, sample_folder)
        image_path = os.path.join(brand_folder_path, sample_folder, 'self_ref', 'screenshot_aft.png')
        with open(image_path, 'rb') as image_file:
            image_data = io.BytesIO(image_file.read())
            img = Image.open(image_data)
            img_hash = str(imagehash.phash(img))

        if img_hash in hashes:
            if img_hash in duplicates:
                duplicates[img_hash].append(sample_folder_path)
            else:
                    duplicates[img_hash] = [hashes[img_hash], sample_folder_path]
        else:
            hashes[img_hash] = sample_folder_path


    if duplicates:
        print(f"{brand_folder} Still has duplicates")
        with open(f'{brand_folder}_duplicates_phash.json', 'w') as json_file:
            json.dump(duplicates, json_file, indent=4)        
        remove_duplicates(f'{brand_folder}_duplicates_phash.json')
    else:
        print(f"{brand_folder} confirm no duplciates")

        
        
