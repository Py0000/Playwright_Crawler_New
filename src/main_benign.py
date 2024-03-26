import asyncio
import argparse
import hashlib
import os
import pandas as pd
import requests

from queue import Queue
from playwright.async_api import async_playwright

import crawler_main as crawler
import util
import util_def

ERROR_URL_FLAG = "Error_Url_Flag"

def write_url_to_file(filename, full_url):
    with open(filename, 'a') as file:
        file.write(full_url + '\n')


def read_domain_from_tranco_csv(csv_path, start_index, end_index):
    df = pd.read_csv(csv_path, header=None)
    selected_range = df.iloc[start_index:end_index, 1].tolist()
    return selected_range


def get_benign_url_from_tranco_domain(domain):
    try:
        https_url = f"https://www.{domain}"
        response = requests.head(https_url, timeout=1, allow_redirects=True)
        response.raise_for_status()
        return https_url
    except requests.RequestException:
        try:
            http_url = f"http://www.{domain}"
            response = requests.head(http_url, timeout=1, allow_redirects=True)
            response.raise_for_status()
            return http_url
        except requests.RequestException:
            return ERROR_URL_FLAG


def get_all_url(domains, filename):
    error_domain_file = f"feeds/benign/benign_error_feeds_{filename}.txt"
    domain_file = f"feeds/benign/benign_feeds_{filename}.txt"
    for domain in domains:
        full_url = get_benign_url_from_tranco_domain(domain)
        if full_url == ERROR_URL_FLAG:
            write_url_to_file(error_domain_file, domain)
        else:
            write_url_to_file(domain_file, full_url)



def benign_crawling_preprocessing(start_index, end_index, filename):
    print("\nPre-Processing Tranco List...")
    csv_path = f"feeds/benign/top-1m.csv"
    domains = read_domain_from_tranco_csv(csv_path, int(start_index), int(end_index))
    get_all_url(domains, filename)
    print("Finished pre-processing Tranco List...")


async def process_current_feed(feed, folder_name):
    dataset_folder_name = f"benign_dataset_{folder_name}"
    await start_crawling(feed, dataset_folder_name)


async def process_benign_feeds(filename):
    benign_file = f"feeds/benign/benign_feeds_{filename}.txt"
    feed_queue = Queue()
    print("\nProcessing feeds from txt file...")
    with open(benign_file, 'r') as file:
        for line in file:
            feed = line.strip()
            feed_queue.put(feed)
    print("Done processing feeds from txt file...")
    
    while not feed_queue.empty():
        feed = feed_queue.get()
        await process_current_feed(feed, filename)


async def start_crawling(feed, dataset_folder_name):
    url_hash = hashlib.sha256(feed.encode()).hexdigest()
    ref_base_folder_path = util.generate_base_folder_for_crawled_dataset(url_hash, dataset_folder_name, ref_flag=True)
    no_ref_base_folder_path = util.generate_base_folder_for_crawled_dataset(url_hash, dataset_folder_name, ref_flag=False)
    try:
        async with async_playwright() as p:
            win_chrome_v116_user_agent = [f"--user-agent={util_def.USER_USER_AGENT_WINDOWS_CHROME}"]
            browser = await p.chromium.launch(headless=True, args=win_chrome_v116_user_agent)

            print("Crawling in progress...")
            print(f"\n------------------------------\nConfiguration: Referrer set\nUrl: {feed}\n-----------------------------")
            await crawler.crawl(browser, feed, url_hash, ref_base_folder_path, timeout_multiplier=4, ref_flag=True)

            print(f"\n------------------------------\nConfiguration: No Referrer set\nUrl: {feed}\n-----------------------------")
            await crawler.crawl(browser, feed, url_hash, no_ref_base_folder_path, timeout_multiplier=4, ref_flag=False)
            print("\nCrawling done...")
        
        if browser:
                await browser.close()

        # Generate a semaphore file to signal that it is ready to be sent to databse
        util.generate_semaphore_lock_file(os.path.join(dataset_folder_name, url_hash))
    except Exception as e:
        print("Error with Playwright: ", e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder name.")
    """
    parser.add_argument("folder_name", help="Name of the folder")
    parser.add_argument("start_index", help="Start range")
    parser.add_argument("end_index", help="End range")
    """
    parser.add_argument("url", help="url of page")
    parser.add_argument("dataset_folder_name", help="name of folder")
    args = parser.parse_args()

    asyncio.run(start_crawling(args.url, args.dataset_folder_name))

    """
    benign_crawling_preprocessing(args.start_index, args.end_index, args.folder_name)
    asyncio.run(process_benign_feeds(args.folder_name))
    print("Program ended!!!")
    """