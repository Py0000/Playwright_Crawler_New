from PIL import Image
import imagehash
import json
import os

screenshot_compare_folder = "_screenshot_comparison"
server_screenshot_file = "screenshot_bef.png"
client_screenshot_file = "screenshot_aft.png"


def save_to_json(file_name, data):
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def compute_phash(image_path):
    try:
        with Image.open(image_path) as img:
            hash_val = imagehash.phash(img)
        return hash_val
    except Exception as e:
        print(e)


def compare_screenshot_bef_aft(main_folder_path, url_index, ref):
    folder_path = os.path.join(main_folder_path, f"{ref}", url_index)

    server_screenshot = os.path.join(folder_path, server_screenshot_file)
    client_screenshot = os.path.join(folder_path, client_screenshot_file)

    server_pHash = compute_phash(server_screenshot) 
    client_pHash = compute_phash(client_screenshot) 

    if client_pHash is None or server_pHash is None:
        diff = "Unable to determine as no hash was computed"
    else:
        diff = server_pHash - client_pHash

    result = {
        "server screenshot pHash": str(server_pHash),
        "client screenshot pHash": str(client_pHash),
        "Difference (server-client)": diff
    }

    return result


def compare_screenshot_different_ref(main_folder_path, url_index, bef_aft_flag):
    ref_folder_path = os.path.join(main_folder_path, "self_ref", url_index)
    no_ref_folder_path = os.path.join(main_folder_path, "no_ref", url_index)
    screenshot_file = server_screenshot_file if bef_aft_flag == "bef" else client_screenshot_file

    ref_pHash = compute_phash(os.path.join(ref_folder_path, screenshot_file))
    no_ref_pHash = compute_phash(os.path.join(no_ref_folder_path, screenshot_file))

    if ref_pHash is None or no_ref_pHash is None:
        diff = "Unable to determine as no hash was computed"
    else:
        diff = ref_pHash - no_ref_pHash

    result = {
        "self ref screenshot pHash": str(ref_pHash),
        "no ref screenshot pHash": str(no_ref_pHash),
        "Difference (ref-no_ref)": diff
    }

    return result

def compare_screenshot(dataset_folder_path, output_path, index):
    self_ref_bef_aft_result = compare_screenshot_bef_aft(dataset_folder_path, index, "self_ref")
    no_ref_bef_aft_result = compare_screenshot_bef_aft(dataset_folder_path, index, "no_ref")
    bef_diff_ref_result = compare_screenshot_different_ref(dataset_folder_path, index, "bef")
    aft_diff_ref_result = compare_screenshot_different_ref(dataset_folder_path, index, "aft")

    result = {
        "Self-ref server and client screenshot comparision": self_ref_bef_aft_result,
        "No-ref server and client screenshot comparision": no_ref_bef_aft_result,
        "Server Self-ref and No-ref screenshot comparison": bef_diff_ref_result,
        "Client Self-ref and No-ref screenshot comparison": aft_diff_ref_result,
    }

    save_to_json(output_path, result)


def generate_screenshot_comparison_report(dataset_folder_path, analyzed_data_path):
    print("\nComparing page screenshot...")
    config_folders = os.listdir(dataset_folder_path)
    indices = []
    for config_folder in config_folders:
        config_folder_path = os.path.join(dataset_folder_path, config_folder)
        url_index_folders = os.listdir(config_folder_path)
        url_index_folders.sort(key=int)
        for index in url_index_folders:
            indices.append(index)
        break      

    for index in indices:
        output_file = f"{index}_screenshot_comparison.json"
        output_folder = os.path.join(analyzed_data_path, screenshot_compare_folder)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        output_path = os.path.join(output_folder, output_file)
        compare_screenshot(dataset_folder_path, output_path, index)
    
    print("Done comparing page screenshot...")




