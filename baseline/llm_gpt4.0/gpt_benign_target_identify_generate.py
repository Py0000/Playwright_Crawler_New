import argparse
import hashlib
import csv 

def compute_sha256(url):
    sha256 = hashlib.sha256()
    sha256.update(url.encode('utf-8'))
    return sha256.hexdigest()


def process_crawled_benign_url(url_file):
    with open(url_file, 'r') as file:
        urls = file.readlines()
    
    range = url_file.split("_")[-1]
    output_file = f"benign_url_hash_pair_{range}.csv"

    with open(output_file, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Url', 'SHA-256 Hash'])

        for url in urls:
            url = url.strip()
            hash = compute_sha256(url)
            writer.writerow([url, hash])



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    parser.add_argument("file_path", help="File name")
    args = parser.parse_args()

    process_crawled_benign_url(args.file_path)