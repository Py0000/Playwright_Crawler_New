import os 
import json
import hashlib
from bs4 import BeautifulSoup, Tag

dom_folder_name = "_dom_comparison"
client_html_file_name = "html_script_aft.html"
server_html_file_name = "html_script_bef.html"
referrers = ["self_ref", "no_ref"]


def get_folder_name(referrer, url_index, main_folder_path):
    return os.path.join(main_folder_path, f"{referrer}", url_index)


def save_to_json(file_name, data):
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_html_script(folder_name, html_file_name):
    with open(os.path.join(folder_name, html_file_name), 'r', encoding='utf-8') as f:
        content = f.read()
        soup = BeautifulSoup(content, 'lxml')
        return soup


def traverse(server_node, client_node, differences, level=0):
    # If node type is different
    if type(server_node) != type(client_node):
        diff_key = f"Level {level} - Node Type Mismatch"
        differences.update({diff_key: {"server": str(server_node), "client": str(client_node)}})
        return

    # If node is a Tag, check its name and attributes
    if isinstance(server_node, Tag) and isinstance(client_node, Tag):
        if server_node.name != client_node.name:
            diff_key = f"Level {level} - Tag Name Mismatch"
            differences.update({diff_key: {"server": server_node.name, "client": client_node.name}})

        elif server_node.attrs != client_node.attrs:
            diff_key = f"Level {level} - Attribute Mismatch"
            differences.update({diff_key: {"server": server_node.attrs, "client": client_node.attrs}})
        
        elif server_node.string != client_node.string:
            diff_key = f"Level {level} - Textual Content Mismatch"
            differences.update({diff_key: {"server": server_node.string, "client": client_node.string}})

        # Continue traversal for children of the Tag
        server_node_children = list(server_node.children)
        client_node_children = list(client_node.children)
        size_of_server_node_children = len(server_node_children)
        size_of_client_node_children = len(client_node_children)

        if size_of_server_node_children != size_of_client_node_children:
            diff_key = f"Level {level} - Children Count Mismatch"
            differences.update({diff_key: {"server": size_of_server_node_children, "client": size_of_client_node_children}})

        max_length = max(size_of_server_node_children, size_of_client_node_children)
        for i in range(max_length):
            if i < size_of_server_node_children and i < size_of_client_node_children:
                traverse(server_node_children[i], client_node_children[i], differences, level+1)
            elif i >= size_of_server_node_children:
                diff_key = f"Level {level+1} - Extra Child in Client"
                differences.update({diff_key: {"client": str(client_node_children[i])}})
            else:
                diff_key = f"Level {level+1} - Extra Child in Server"
                differences.update({diff_key: {"server": str(server_node_children[i])}})



def compute_hash(file_path, algorithm='sha256'):
    """Compute hash of a file using the given algorithm."""
    h = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        # Reading in chunks in case of large files
        for chunk in iter(lambda: f.read(4096), b''):
            h.update(chunk)
    return h.hexdigest()



def compare_dom_bef_aft(main_folder_path, url_index, output_folder, ref):
    folder_name = get_folder_name(ref, url_index, main_folder_path)

    bef_hash = compute_hash(os.path.join(folder_name, server_html_file_name))
    aft_hash = compute_hash(os.path.join(folder_name, client_html_file_name))
    is_hash_same = bef_hash == aft_hash

    bef_html = load_html_script(folder_name, server_html_file_name)
    aft_html = load_html_script(folder_name, client_html_file_name)

    diff = {}
    traverse(bef_html, aft_html, diff)
    is_dom_same = len(diff) == 0

    if (len(diff) == 0):
        sorted_diff = {"Message": "No difference between html DOM of the 2 files"}
    else:
        sorted_diff = dict(sorted(diff.items(), key=lambda item: int(item[0].split()[1])))
    
    output_path = os.path.join(output_folder, f"{ref}_bef_aft_html_dom_comparision.json")
    save_to_json(output_path, sorted_diff)

    return is_dom_same, is_hash_same


def compare_dom_different_ref(index, main_folder_path, output_folder, bef_aft_script):
    
    ref_folder = get_folder_name(referrers[0], index, main_folder_path)  
    no_ref_folder = get_folder_name(referrers[1], index, main_folder_path)

    ref_hash = compute_hash(os.path.join(ref_folder, bef_aft_script))
    no_ref_hash = compute_hash(os.path.join(no_ref_folder, bef_aft_script))
    is_hash_same = ref_hash == no_ref_hash

    ref_html = load_html_script(ref_folder, bef_aft_script)
    no_ref_html = load_html_script(no_ref_folder, bef_aft_script)

    diff = {}
    traverse(ref_html, no_ref_html, diff)
    is_dom_same = len(diff) == 0

    if (len(diff) == 0):
        sorted_diff = {"Message": "No difference between html DOM of the 2 files"}
    else:
        sorted_diff = dict(sorted(diff.items(), key=lambda item: int(item[0].split()[1])))

    bef_aft_tag = "aft" if "aft" in bef_aft_script else "bef"
    output_path = os.path.join(output_folder, f"self_ref_no_ref_{bef_aft_tag}_dom_comparision.json")
    save_to_json(output_path, sorted_diff)
    
    return is_dom_same, is_hash_same


def compare_dom(index, main_folder_path, output_folder):
    bef_aft_ref_dom, bef_aft_ref_hash = compare_dom_bef_aft(main_folder_path, index, output_folder, referrers[0])
    bef_aft_no_ref_dom, bef_aft_no_ref_hash = compare_dom_bef_aft(main_folder_path, index, output_folder, referrers[1])
    diff_ref_bef_dom, diff_ref_bef_hash = compare_dom_different_ref(index, main_folder_path, output_folder, server_html_file_name)
    diff_ref_aft_dom, diff_ref_aft_hash = compare_dom_different_ref(index, main_folder_path, output_folder, client_html_file_name)

    result = {
        "Is DOM for Before and After (Self-ref) same?": bef_aft_ref_dom,
        "Is DOM for Before and After (No-ref) same?": bef_aft_no_ref_dom,
        "Is HTML file HASH for Before and After (Self-ref) same?": bef_aft_ref_hash,
        "Is HTML file HASH for Before and After (No-ref) same?": bef_aft_no_ref_hash,
        "Is DOM for Self-ref vs No-ref (Before) same?": diff_ref_bef_dom,
        "Is DOM for Self-ref vs No-ref (After) same?": diff_ref_aft_dom,
        "Is HTML file HASH for Self-ref vs No-ref (Before) same?": diff_ref_bef_hash,
        "Is HTML file HASH for Self-ref vs No-ref (After) same?": diff_ref_aft_hash,
    }

    output_path = os.path.join(output_folder, f"summarized.json")
    save_to_json(output_path, result)


def generate_dom_comparison_data(dataset_folder_path, analyzed_data_path):
    print("\nComparing dom structure...")
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
        output_folder = os.path.join(analyzed_data_path, dom_folder_name, index)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        compare_dom(index, dataset_folder_path, output_folder)
    print("Done comparing dom structure...")

