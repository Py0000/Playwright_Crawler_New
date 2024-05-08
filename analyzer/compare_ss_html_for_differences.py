import hashlib
import shutil
import pandas as pd
import os
from shutil import copy2
import zipfile
import json
import PIL.Image
from tqdm import tqdm

'''
General Purpose: Extract, compare, and organize screenshots and HTML files from phishing datasets
- Compares self_ref vs no_ref screenshots and HTML files.
- Extract only those pairs where the screenshots differ.
'''

dataset_path = "datasets"
months = ["Oct", "Nov", "Dec"]
phishing_folders_oct = ["251023", "261023", "271023", "281023", "291023", "301023"] # oct
phishing_folders_nov = ["011123", "091123", "101123", "111123", "121123", "131123", "141123", "151123", "161123", "171123", "181123", "191123", "201123", "211123", "221123", "231123", "241123", "251123", "261123", "271123", "291123", "301123"]
phishing_folders_dec = ["011223", "021223", "031223", "041223", "051223", "061223", "071223", "081223", "091223", "101223", "111223", "121223", "131223", "141223", "151223", "161223", "171223", "181223", "191223", "201223", "211223", "221223", "231223", "241223", "251223"]

phishing_folder = phishing_folders_dec
month = "Dec"
for date in tqdm(phishing_folder):
    path = os.path.join("datasets", month, f"dataset_{date}", f"dataset_{date}", f"dataset_{date}", "complete_dataset")
    target_ss_path = os.path.join("comparison", "screenshots", f"dataset_{date}")
    target_html_path = os.path.join("comparison", "htmls", f"dataset_{date}")

    if not os.path.exists(target_ss_path):
        os.makedirs(target_ss_path)
    
    if not os.path.exists(target_html_path):
        os.makedirs(target_html_path)
    
    for folder in os.listdir(path):
        if not folder.endswith(".zip"):
            continue

        hash = folder.replace(".zip", "")
        with zipfile.ZipFile(os.path.join(path, folder), 'r') as zip_ref:
            ref_ss_rel_path = os.path.join('self_ref', 'screenshot_aft.png')
            no_ref_ss_rel_path = os.path.join('no_ref', 'screenshot_aft.png')

            ref_ss_path = next((zipinfo.filename for zipinfo in zip_ref.infolist() if ref_ss_rel_path in zipinfo.filename), None)
            no_ref_ss_path = next((zipinfo.filename for zipinfo in zip_ref.infolist() if no_ref_ss_rel_path in zipinfo.filename), None)

            if ref_ss_path and no_ref_ss_path:
                with zip_ref.open(ref_ss_path, 'r') as image_file:
                    ref_image_data = image_file.read()
                    ref_hash_func = hashlib.sha256()
                    ref_hash_func.update(ref_image_data)
                    ref_img_hash = ref_hash_func.hexdigest()
                with zip_ref.open(no_ref_ss_path, 'r') as image_file:
                    no_ref_image_data = image_file.read()
                    no_ref_hash_func = hashlib.sha256()
                    no_ref_hash_func.update(no_ref_image_data)
                    no_ref_img_hash = no_ref_hash_func.hexdigest()
                
                if ref_img_hash != no_ref_img_hash:
                    zip_ref.extract(ref_ss_path, target_ss_path)
                    ref_original_screenshot_path = os.path.join(target_ss_path, ref_ss_path)
                    ref_new_screenshot_path = os.path.join(target_ss_path, f"{hash}_ref.png")

                    zip_ref.extract(no_ref_ss_path, target_ss_path)
                    no_ref_original_screenshot_path = os.path.join(target_ss_path, no_ref_ss_path)
                    no_ref_new_screenshot_path = os.path.join(target_ss_path, f"{hash}_no_ref.png")

                    shutil.copy(ref_original_screenshot_path, ref_new_screenshot_path)
                    shutil.copy(no_ref_original_screenshot_path, no_ref_new_screenshot_path)
                    try:
                        os.remove(ref_original_screenshot_path)
                        os.removedirs(os.path.dirname(ref_original_screenshot_path))
                        os.remove(no_ref_original_screenshot_path)
                        os.removedirs(os.path.dirname(no_ref_original_screenshot_path))
                    except:
                        pass

                    ref_html_relative_path = os.path.join('self_ref', 'html_script_aft.html')
                    ref_html_file_path = next((zipinfo.filename for zipinfo in zip_ref.infolist() if ref_html_relative_path in zipinfo.filename), None)
                    no_ref_html_relative_path = os.path.join('no_ref', 'html_script_aft.html')
                    no_ref_html_file_path = next((zipinfo.filename for zipinfo in zip_ref.infolist() if no_ref_html_relative_path in zipinfo.filename), None)
                    
                    try:
                        if ref_html_file_path and no_ref_html_file_path:
                            zip_ref.extract(ref_html_file_path, target_html_path)
                            ref_original_html_path = os.path.join(target_html_path, ref_html_file_path)
                            ref_new_html_path = os.path.join(target_html_path, f"{hash}_ref.html")

                            zip_ref.extract(no_ref_html_file_path, target_html_path)
                            no_ref_original_html_path = os.path.join(target_html_path, no_ref_html_file_path)
                            no_ref_new_html_path = os.path.join(target_html_path, f"{hash}_no_ref.html")

                            shutil.copy(ref_original_html_path, ref_new_html_path)
                            shutil.copy(no_ref_original_html_path, no_ref_new_html_path)
                            try:
                                os.remove(ref_original_html_path)
                                os.remove(no_ref_original_html_path)
                                os.removedirs(os.path.dirname(ref_original_html_path))
                                os.removedirs(os.path.dirname(no_ref_original_html_path))
                            except:
                                pass
                    except:
                        pass