import asyncio
import argparse
import aiohttp
import hashlib
import os

from playwright.async_api import async_playwright

import crawler_main as crawler
import util
import util_def

feeds_queue = asyncio.Queue()
OPENPHISH_FEEDS_URL = "https://opfeeds.s3-us-west-2.amazonaws.com/OPBL/phishing_blocklist.txt"



async def fetch_openphish_feeds(feeds_filename):
    print("Fetching feeds")
    while True:
        print("Establish connection with OpenPhish")
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(OPENPHISH_FEEDS_URL) as response:
                    print("Connection established with OpenPhish")
                    if response.status == 200:
                        print("Feeds obtain. Parsing...")
                        feeds = await response.text()
                        urls = feeds.splitlines()
                        for url in urls:  
                            await feeds_queue.put(url)
                        feeds_path = f"feeds/urls/openphish_feeds_{feeds_filename}.txt"
                        with open(feeds_path, 'a') as file:
                            file.write(feeds)
                    else:
                         print(f"Error fetching feeds. HTTP status: {response.status}")
            
            except Exception as e:
                print("Error fetching feeds from url: ", e)

            finally:
                print("Awaitng for 5 mins for next set of feeds...")
                await asyncio.sleep(300) # waits for 1 minute before the next fetch



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
            await crawler.crawl(browser, seed_url, url_hash, ref_base_folder_path, timeout_multiplier=1, ref_flag=True)

            print(f"\n------------------------------\nConfiguration: No Referrer set\nUrl: {seed_url}\n-----------------------------")
            await crawler.crawl(browser, seed_url, url_hash, no_ref_base_folder_path, timeout_multiplier=1, ref_flag=False)
            print("\nCrawling done...")

            if browser:
                await browser.close()
            
            # Generate a semaphore file to signal that it is ready to be sent to databse
            util.generate_semaphore_lock_file(os.path.join(dataset_folder_name, url_hash))
    except Exception as e:
        print("Error with Playwright: ", e)


async def process_current_feed(feed, folder_name):
    dataset_folder_name = f"{util_def.FOLDER_DATASET_BASE}_{folder_name}"
    await start_crawling(feed, dataset_folder_name)


async def process_feeds_from_queue(folder_name):
    while True:
        print("Processing feeds")
        feed_to_process = await feeds_queue.get()
        await process_current_feed(feed_to_process, folder_name)
        feeds_queue.task_done()


async def main(folder_name):
    await asyncio.gather(
        fetch_openphish_feeds(folder_name),
        process_feeds_from_queue(folder_name)
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder name.")
    parser.add_argument("folder_name", help="Name of the folder")
    args = parser.parse_args()

    asyncio.run(main(args.folder_name))
    print("Program ended!!!")