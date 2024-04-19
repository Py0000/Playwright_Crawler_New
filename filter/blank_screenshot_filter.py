import os
import shutil

blank_screenshot_list = [] 




month = "Oct"
dates = ["251023"]
for date in dates:
    print(f"\nProcessing {date}")
    dataset_folder_path = os.path.join("datasets", month, f"dataset_{date}", f"dataset_{date}", f"dataset_{date}", "complete_dataset")

    with open(os.path.join(f"blank_hashes_{date}.txt"), 'r') as file:
        for line in file:
            blank_screenshot_list.append(line.strip())

    blank_screenshot_folder = os.path.join(dataset_folder_path, "blank_screenshot")
    if not os.path.exists(blank_screenshot_folder):
        os.makedirs(blank_screenshot_folder)

    for folder in os.listdir(dataset_folder_path):
        if not folder.endswith(".zip"):
            continue

        folder_hash = folder.replace(".zip", "")
        if folder_hash in blank_screenshot_list:
            print(folder_hash)
            file_path = os.path.join(dataset_folder_path, folder)
            shutil.move(file_path, blank_screenshot_folder)


