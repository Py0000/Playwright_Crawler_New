import asyncio
import argparse
import aiohttp
import hashlib
import os

from playwright.async_api import async_playwright

import crawler_main as crawler
import util
import util_def


async def start_crawling(feed, dataset_folder_name):
    seed_url = feed
    url_hash = hashlib.sha256(seed_url.encode()).hexdigest()
    ref_base_folder_path = util.generate_base_folder_for_crawled_dataset(url_hash, dataset_folder_name, ref_flag=True)
    no_ref_base_folder_path = util.generate_base_folder_for_crawled_dataset(url_hash, dataset_folder_name, ref_flag=False)
    try:
        async with async_playwright() as p:
            win_chrome_v116_user_agent = [f"--user-agent={util_def.USER_USER_AGENT_WINDOWS_CHROME}"]
            browser = await p.chromium.launch(headless=True, args=win_chrome_v116_user_agent)

            print("Crawling in progress...")
            print(f"\n------------------------------\nConfiguration: Referrer set\nUrl: {seed_url}\n-----------------------------")
            await crawler.crawl(browser, seed_url, url_hash, ref_base_folder_path, timeout_multiplier=2, ref_flag=True)

            print(f"\n------------------------------\nConfiguration: No Referrer set\nUrl: {seed_url}\n-----------------------------")
            await crawler.crawl(browser, seed_url, url_hash, no_ref_base_folder_path, timeout_multiplier=2, ref_flag=False)
            print("\nCrawling done...")

            if browser:
                await browser.close()
            
            # Generate a semaphore file to signal that it is ready to be sent to databse
            util.generate_semaphore_lock_file(os.path.join(dataset_folder_name, url_hash))
    except Exception as e:
        print("Error with Playwright: ", e)


async def process_current_feed(feed, folder_name):
    dataset_folder_name = f"recrawl_{util_def.FOLDER_DATASET_BASE}_{folder_name}"
    await start_crawling(feed, dataset_folder_name)




async def main(folder_name, file_name):
    with open(file_name, 'r') as file:
        urls = file.readlines()

    urls = [url.strip() for url in urls]

    for url in urls:
        await process_current_feed(url, folder_name)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder name.")
    parser.add_argument("folder_name", help="Name of the folder")
    parser.add_argument("file_name", help="Name of the feeds file")
    args = parser.parse_args()

    asyncio.run(main(args.folder_name, args.file_name))
    print("Program ended!!!")