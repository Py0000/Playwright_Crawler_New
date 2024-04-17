import json
import os

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

import util_def

async def save_screenshot(page, folder_path, file_name):
    # Insurance code to guarantee that page is really loaded before taking screenshot
    try:
        await page.wait_for_load_state('networkidle')
    except:
        await page.wait_for_timeout(5000)

    path = os.path.join(os.getcwd(),folder_path, file_name)
    try: 
        await page.screenshot(path=path, full_page=True)
        print("Screenshot Captured...")
        status = "Success"
    except: 
        print("Unable to capture screenshot...")
        status = "Failed"
    finally:
        return status



def save_html_script(folder_path, file_name, content):
    file_path = os.path.join(os.getcwd(), folder_path, file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("HTML script Save Successfully...")


async def extract_links(folder_path, soup, page, base_url):
    file_path = os.path.join(os.getcwd(), folder_path, util_def.FILE_EMBEDDED_URL)
    await get_link_in_iframe(file_path, soup, page, set(), base_url)

    return file_path


async def get_link_in_iframe(file_path, soup, page, added_url_set, base_url):
    for iframe in soup.find_all('iframe'):
        iframe_src = iframe.attrs.get('src')  # Load the iframe 
        
        if not iframe_src:
            continue

        # Checks if the iframe contains legitimate url
        parsed_url = urlparse(iframe_src)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            continue

        added_url_set = save_embedded_url(file_path, iframe_src, base_url, added_url_set)
        await page.goto(iframe_src)
        iframe_soup = BeautifulSoup(await page.content(), 'lxml')
        added_url_set = await handle_nested_iframes(iframe_soup, file_path, page, added_url_set, base_url)


async def handle_nested_iframes(iframe_soup, file_path, page, added_url_set, base_url):
    for a in iframe_soup.find_all('a'):
        url = a.get("href")
        added_url_set = save_embedded_url(file_path, url, base_url, added_url_set)
    
    added_url_set = await get_link_in_iframe(file_path, iframe_soup, page, added_url_set, base_url)
    return added_url_set


def save_embedded_url(file_path, url, base_url, added_url_set):
    
    try: 
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            if urlparse(base_url).scheme:
                url = urljoin(base_url, url)

        if url not in added_url_set:
            with open(file_path, "a") as f:
                f.write(url + '\n')
                added_url_set.add(url)
    except:
        pass

    return added_url_set



def save_more_detailed_network_logs(folder_path, data):
    print("Saving more detailed network logs...")
    try:
        file_dir = os.path.join(folder_path, util_def.FILE_DETAILED_NETWORK)
        with open(file_dir, 'w') as file:
            json.dump(data, file, indent=4)
        status = "Success"
    except:
        status = "Failed"
    finally:
        return status
    


# Get client-side scripts
client_side_scripts_injection_code = '''() => {
    const scripts = [];
    const scriptElements = document.querySelectorAll('script');
    scriptElements.forEach(script => {
        if (script.src) {
            scripts.push(script.src);
        } else {
            scripts.push(script.innerText);
        }
    });
    return scripts;
}'''


def save_client_side_script(folder_path, data):
    file = os.path.join(os.getcwd(), folder_path, util_def.FILE_CLIENT_SIDE_SCRIPT)

    # Save data to a JSON file
    with open(file, 'w') as json_file:
        json.dump(data, json_file, indent=4)

