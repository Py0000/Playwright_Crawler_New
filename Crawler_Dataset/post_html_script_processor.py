from bs4 import BeautifulSoup 
import os 
import json 
from urllib.parse import urljoin, urlparse

BEFORE_CLIENT_SIDE_RENDERING_INDICATOR = "Before client-side rendering"
AFTER_CLIENT_SIDE_RENDERING_INDICATOR = "After client-side rendering"

FILE_HTML_SCRIPT_AFT = "html_script_aft.html"
FILE_HTML_SCRIPT_BEF = "html_script_bef.html"
FILE_HTML_TAG = "html_tag.json"
FILE_EMBEDDED_URL = "embedded_url.txt"
FILE_CRAWL_LOG_INFO = "log.json"

CURRENT_COVERED_TAG_SET = {'title', 
                           'form', 'input', 'textarea', 'button', 'select', 'output',
                           'iframe',
                           'style', 'span', 'hr',
                           'img', 'audio', 'video', 'svg', 'picture', 'source', 'track', 'map', 'canvas',
                           'a', 'link', 'nav',
                           'script', 'noscript', 'embed', 'object', 'code',
                           'ul', 'ol', 'dl', 'dt', 'dd',
                           'table',
                           'head', 'meta', 'base', 'bpdy', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'body',
                           'div', 'header', 'footer', 'main', 'section', 'article', 'aside', 'details', 'dialog', 'data',
                           'br', 'html',
                           'abbr', 'b', 'bdi', 'bdo', 'blockquote', 'cite', 'del', 'dfn', 'em', 'i', 'ins', 'kbd',
                           'mark', 'pre', 'q', 's', 'small', 'samp', 'strong', 'sup', 'sub', 'u', 'var',
                           'meter', 'progress',
                           'template',
                        }

CURRENT_KNOWN_EXCLUEDED_TAG_SET = {
    'optgroup', 'option', 'label', 'fieldset', 'legend', 'datalist', 'area', 'figcaption', 'figure', 
    'li', 'caption', 'th', 'tr', 'td', 'thead', 'tbody', 'tfoot', 'col', 'colgroup', 'summary', 'param',
}

def read_html_content_to_soup(file_location):
    ERROR_FLAG = "ERROR"
    ERROR_INDICATOR = "Error occurred for url:"
    server_html_script_path = os.path.join(file_location, FILE_HTML_SCRIPT_BEF)
    with open(server_html_script_path, 'r', encoding='utf-8') as f:
        server_file_content = f.read()
        if ERROR_INDICATOR in server_file_content:
            server_soup = ERROR_FLAG
        else:
            server_soup = BeautifulSoup(server_file_content, 'lxml')
    
    client_html_script_path = os.path.join(file_location, FILE_HTML_SCRIPT_AFT)
    with open(client_html_script_path, 'r', encoding='utf-8') as f:
        client_file_content = f.read()
        if ERROR_INDICATOR in client_file_content:
            client_soup = ERROR_FLAG
        else:
            client_soup = BeautifulSoup(client_file_content, 'lxml')
    
    return server_soup, client_soup


def get_unique_html_tags(soup):
    set = {tag.name for tag in soup.find_all()}
    initial_diff = set.difference(CURRENT_COVERED_TAG_SET)
    diff = initial_diff.difference(CURRENT_KNOWN_EXCLUEDED_TAG_SET)

    if len(diff) == 0:
        diff = ""

    return str(diff)


def save_unique_html_tags(folder_path, server_data, client_data):
    data = {
        BEFORE_CLIENT_SIDE_RENDERING_INDICATOR: server_data,
        AFTER_CLIENT_SIDE_RENDERING_INDICATOR: client_data
    }
    
    file_path = os.path.join(os.getcwd(), folder_path, FILE_HTML_TAG)
    with open(file_path, 'a', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)



# current_data_folder = dest_folder + folder = Phishing/dataset + hash(url)
def extract_unique_html_tags(current_data_folder, ref_flag):
    ref_folder = "self_ref" if ref_flag else "no_ref"
    ref_folder_path = os.path.join(current_data_folder, ref_folder)
    server_html_soup, client_html_soup = read_html_content_to_soup(ref_folder_path)
    if server_html_soup == "ERROR":
        server_html_tag = "Error during crawling"
    else:
        server_html_tag = get_unique_html_tags(server_html_soup)

    if client_html_soup == "ERROR":
        client_html_tag = "Error during crawling"
    else:
        client_html_tag = get_unique_html_tags(client_html_soup)

    save_unique_html_tags(ref_folder_path, server_html_tag, client_html_tag)



def get_currently_saved_embedded_url(embedded_url_file_path):
    url_set = set()
    if os.path.exists(embedded_url_file_path):
        with open(embedded_url_file_path, 'r') as f:
            for line in f:
                url = line.strip()
                url_set.add(url)
    
    return url_set


def get_base_url(current_page_folder_path):
    log_file_path = os.path.join(current_page_folder_path, FILE_CRAWL_LOG_INFO)
    with open(log_file_path, 'r') as f:
        data = json.load(f)
        base_url = data.get("Url visited", None)  # Returns None if the key doesn't exist
    return base_url


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


def get_link_in_anchor(file_path, soup, added_url_set, base_url):
    for a in soup.find_all("a"):
        url = a.get("href")
        added_url_set = save_embedded_url(file_path, url, base_url, added_url_set)


def extract_anchored_links(current_data_folder, ref_flag):
    ref_folder = "self_ref" if ref_flag else "no_ref"
    ref_folder_path = os.path.join(current_data_folder, ref_folder)
    file_path = os.path.join(os.getcwd(), current_data_folder, ref_folder, FILE_EMBEDDED_URL)
    _, client_html_soup = read_html_content_to_soup(ref_folder_path)

    if client_html_soup != "ERROR":
        # Extract links from anchor tags
        base_url = get_base_url(ref_folder_path)
        added_url_set = get_currently_saved_embedded_url(file_path)
        get_link_in_anchor(file_path, client_html_soup, added_url_set, base_url)


def post_process_html_script(current_data_folder):
    print("Extracting unique html tags...")
    extract_unique_html_tags(current_data_folder, ref_flag=True)
    extract_unique_html_tags(current_data_folder, ref_flag=False)

    print("Extracting anchored links...")
    extract_anchored_links(current_data_folder, ref_flag=True)
    extract_anchored_links(current_data_folder, ref_flag=False)


    

