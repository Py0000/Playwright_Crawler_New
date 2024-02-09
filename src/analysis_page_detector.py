import json
import os
import re
from bs4 import BeautifulSoup


HTML_FILE_AFTER = "html_script_aft.html"
HTML_FILE_BEFORE = "html_script_bef.html"
BASE_FOLDER_NAME = "_page_error_info"
BASE_FILE_NAME = "page_info.json"

ERROR_TYPE_BLOCKED = "Access Blocked"
ERROR_TYPE_INVALID = "Page is Invalid"
ERROR_TYPE_BLANK = "Blank Page"
ERROR_TYPE_CONNECTION = "connection error"

def get_invalid_types():
    ERROR_TYPE_SERVICE_NOT_AVAILABLE = r"service (.+?) is not available"
    ERROR_TYPE_SLEEPING = [r"website.*sleeping", r"webpage.*sleeping", r"page.*sleeping", r"site.*sleeping"]
    ERROR_TYPE_ELIMINATED = [r"website.eliminated", r"webpage.*eliminated", r"page.*eliminated", r"site.*eliminated"]
    ERROR_TYPE_DELETED = [r"website.deleted", r"webpage.*deleted", r"page.*deleted", r"site.*deleted"]
    ERROR_TYPE_NOT_FOUND = [r"site.*(not found)", r"page.*(not found)", r"website.*(not found)", r"webpage.*(not found)"]
    ERROR_TYPE_NO_LONGER_EXISTS = "no longer exist"
    ERROR_TYPE_UNDER_CONSTRUCTION = "under construction"
    ERROR_TYPE_UNAVAILABLE = "temporarily unavailable"
    ERROR_TYPE_404 = r"404(.*not found)?"
    ERROR_TYPE_SHIFTED_DOMAIN = ["default web site page", "default page", "default website", "default webpage"]

    INVALID_ERRORS = []

    INVALID_ERRORS.append(ERROR_TYPE_SERVICE_NOT_AVAILABLE)
    INVALID_ERRORS.extend(ERROR_TYPE_SLEEPING)
    INVALID_ERRORS.extend(ERROR_TYPE_ELIMINATED)
    INVALID_ERRORS.extend(ERROR_TYPE_DELETED)
    INVALID_ERRORS.extend(ERROR_TYPE_NOT_FOUND)
    INVALID_ERRORS.append(ERROR_TYPE_NO_LONGER_EXISTS)
    INVALID_ERRORS.append(ERROR_TYPE_UNDER_CONSTRUCTION)
    INVALID_ERRORS.append(ERROR_TYPE_UNAVAILABLE)
    INVALID_ERRORS.append(ERROR_TYPE_404)
    INVALID_ERRORS.extend(ERROR_TYPE_SHIFTED_DOMAIN)

    return INVALID_ERRORS


def get_blocked_errors_type():
    ERROR_TYPE_403 = r"403(.*forbidden)?"
    ERROR_TYPE_ACCESS_DENIED = "access denied"
    ERROR_TYPE_NOT_ALLOWED = "not allowed"
    ERROR_TYPE_509_BANDWIDTH_LIMIT_EXCEED = "509 bandwidth limit exceeded"
    ERROR_TYPE_BLOCKED = "blocked"
    ERROR_TYPE_NOT_AUTHORIZED = ["not authorized", "not authorised", "unauthorized", "unauthorised"]
    ERROR_TYPE_ERROR_429 = "HTTP/2 429"
    ERROR_TYPE_SUSPECTED_PHISHING = "suspected phishing site"

    BLOCKED_ERRORS = []

    BLOCKED_ERRORS.append(ERROR_TYPE_403)
    BLOCKED_ERRORS.append(ERROR_TYPE_ACCESS_DENIED)
    BLOCKED_ERRORS.append(ERROR_TYPE_NOT_ALLOWED)
    BLOCKED_ERRORS.append(ERROR_TYPE_509_BANDWIDTH_LIMIT_EXCEED)
    BLOCKED_ERRORS.append(ERROR_TYPE_BLOCKED)
    BLOCKED_ERRORS.append(ERROR_TYPE_SUSPECTED_PHISHING)
    BLOCKED_ERRORS.append(ERROR_TYPE_ERROR_429)
    BLOCKED_ERRORS.extend(ERROR_TYPE_NOT_AUTHORIZED)

    return BLOCKED_ERRORS


def determine_error_type(html_script):
    BLOCK_ERRORS = get_blocked_errors_type()
    UNAVAILABLE_ERRORS = get_invalid_types()

    all_text_in_html = html_script.get_text().lower()

    for pattern in BLOCK_ERRORS:
        if re.search(pattern, all_text_in_html):
            return pattern
    
    for pattern in UNAVAILABLE_ERRORS:
        if re.search(pattern, all_text_in_html):
            return pattern


def is_page_blank_or_error(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # The first half of this functions checks for error page
    if content.startswith("Error occurred for url: "):
        return True, ERROR_TYPE_CONNECTION
    
    html_script = BeautifulSoup(content, 'lxml')
    has_error_type = determine_error_type(html_script)
    if (has_error_type != None):
        return True, has_error_type

    # The second half of this functions checks for blank page
    # Remove script and style content as they don't affect visual representation
    # Avoids false negative
    for script in html_script(["script", "style"]):
        script.extract()
    
    # Check for text content
    if html_script.get_text(strip=True):
        return False, None

    # Check for tags other than html, head, and body
    significant_tags = [tag for tag in html_script.find_all(True) if tag.name not in ['html', 'head', 'body']]
    if significant_tags:
        return False, None

    return True, ERROR_TYPE_BLANK


def generate_page_error_analysis_report(dataset_folder_path, html_filename, analyzed_data_path):
    # Get a list of all items in the main_folder
    config_folders = os.listdir(dataset_folder_path)
    problem_html = {config: {} for config in config_folders}

    # Iterate through each item
    for config_folder in problem_html.keys():
        config_folder_path = os.path.join(dataset_folder_path, config_folder)
        url_index_folders = os.listdir(config_folder_path)
        url_index_folders.sort(key=int)

        for url_index_folder in url_index_folders:
            url_index_folder_path = os.path.join(config_folder_path, url_index_folder)
            html_file_path = os.path.join(url_index_folder_path, html_filename)
        
            if (os.path.exists(html_file_path)):
                    result, type = is_page_blank_or_error(html_file_path)
                    if (result):
                        problem_html[config_folder].update({url_index_folder: type})
                        
        problem_html[config_folder].update({"Total Count": len(problem_html[config_folder])})
        
    tag = "aft" if "aft" in html_filename else "bef"
    output_folder_path = os.path.join(analyzed_data_path, BASE_FOLDER_NAME)
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
        
    with open(os.path.join(output_folder_path, f"{tag}_{BASE_FILE_NAME}"), "w", encoding="utf-8") as f:
        json.dump(problem_html, f, ensure_ascii=False, indent=4)


def generate_page_analysis_report(dataset_folder_path, analyzed_data_path):
    print("\nDetecting error, invalid & blank pages...")
    generate_page_error_analysis_report(dataset_folder_path, HTML_FILE_AFTER, analyzed_data_path)
    generate_page_error_analysis_report(dataset_folder_path, HTML_FILE_BEFORE, analyzed_data_path)
    print("Done detecting error, invalid & blank pages...")


