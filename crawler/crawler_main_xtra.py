import asyncio
import os 
import time
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from datetime import datetime
from playwright.async_api import async_playwright

import crawler_actions
import crawler_certificate_extractor as certificate_extractor
import crawler_dns_extractor as dns_extractor
import crawler_utilities
import util
import util_def 

'''
Used for crawling benign pages required for training VisualPhishNet
'''

ERROR_MSG = "Error visiting page"

# coroutine: special type of function that can pause its execution and yield control back to the event loop, allowing other tasks to run concurrently
# args & kwargs: variable number of arguments of a function
async def timeout_wrapper(coroutine, *args, default_values, timeout=10, **kwargs):
    try:
        return await asyncio.wait_for(coroutine(*args, **kwargs), timeout)
    except asyncio.TimeoutError:
        print(f"Timeout occurred while executing {coroutine.__name__}.")
        return default_values
    


# Waits for page to complete loading 
async def wait_for_page_to_load(page):
    await crawler_actions.move_mouse_smoothly(page)
    try:
        # Wait for the page to load completely (wait for the dom contentload event)
        await page.wait_for_load_state('domcontentloaded')
    except:
        await page.wait_for_timeout(2000)

    try:
        # Wait for the page to no more network interaction
        await page.wait_for_load_state('networkidle')
    except:
        await page.wait_for_timeout(5000)


# Sets the playwright page referrer to the url provided if ref_flag is set.
# Otherwise, set it to None (i.e. Empty)
async def set_page_referrer(page, ref_flag, to_visit_url):
    if ref_flag:
        await page.set_extra_http_headers({"Referer": to_visit_url})


# dataset_folder_name: refers to the name of the (base)folder to store the crawled data
async def crawl(browser, url, url_hash, folder_path, timeout_multiplier, ref_flag):
    timeout_limit = 10 * timeout_multiplier
    start_time = time.time()
    time_crawled = datetime.now()

    try:
        context = await browser.new_context()
        page = await context.new_page()
        await set_page_referrer(page, ref_flag, url)
        
        main_http_status = "Not Visited"
        timeout_task = None
        print("[Client-Side] Context & Page setup done...")

        # To capture number of redirection of url that occurred
        redirect_info = {
            'count': 0,
            'error': None
        }

        def on_response(response):
            nonlocal redirect_count
            if 300 <= response.status < 400:
                redirect_info['count'] += 1

        print("[Client-Side] Visiting Url...")
        page.on("response", on_response)
        response = await page.goto(url, timeout=(17000 * timeout_multiplier))
        
        print("[Client-Side] Waiting for page to load...")
        await wait_for_page_to_load(page)

        visited_url = page.url # See if url changes after visiting the page.
        if response:
            main_http_status = response.status

        print("[Client-Side] Executing user action...")
        client_move_status = await timeout_wrapper(
            crawler_actions.execute_user_action, 
            page, 
            timeout=1,  
            default_values="Timeout"
        )

        print("[Client-Side] Saving Screenshot...")
        client_screenshot_status = await timeout_wrapper(
            crawler_utilities.save_screenshot, 
            page, folder_path, util_def.FILE_SCREENSHOT_AFT, 
            timeout=timeout_limit,  
            default_values="Timeout"
        )

        html_content = await page.content()
        soup = BeautifulSoup(html_content, "lxml")
        
        '''
        urls = []
        urls.append(url)
        links = soup.find_all('a')
        for link in links:
            if link.get('href') is not None:
                current_url = link.get('href')
                parsed_url = urlparse(current_url)
                if not parsed_url.scheme:
                    current_url = urljoin(url, current_url)
                if current_url not in urls:
                    urls.append(current_url)
        print("\nUrls:\n", urls)
        '''
        print("[Client-Side] Saving HTML script...")
        content = soup.prettify()
        if content is not None:
            crawler_utilities.save_html_script(folder_path, util_def.FILE_HTML_SCRIPT_AFT, content)
            await crawler_utilities.extract_links(folder_path, soup, page, visited_url)
        
        client_html_script_status = "Success"

        print("Actual url: ", url)
        print("Url visited: ", visited_url)
        user_agent = await timeout_wrapper(
            page.evaluate, 
            '''() => window.navigator.userAgent''', 
            timeout=timeout_limit, 
            default_values="Timeout"
        )
        referrer = await timeout_wrapper(
            page.evaluate, 
            '''() => document.referrer''', 
            timeout=timeout_limit, 
            default_values="Timeout"
        )
        print("User-Agent:", user_agent)
        print("Referrer: ", referrer)
        
    
    except Exception as e:
        print(e)
        crawler_utilities.save_html_script(folder_path, util_def.FILE_HTML_SCRIPT_AFT, f"Error occurred for url: {url}\n{e}")
        client_html_script_status = "Failed"

        visited_url = url
        client_move_status = ERROR_MSG
        client_html_script_status = ERROR_MSG
        client_screenshot_status = ERROR_MSG
        redirect_info['error'] = ERROR_MSG
    
    finally:
        end_time = time.time()
        if page:
            print("[Main Crawler: finally] Closing page...")
            await page.close()
        if context:
            print("[Main Crawler: finally] Closing context...")
            await context.close()
        if timeout_task and not timeout_task.done():
            try:    
                await timeout_task
            except:
                pass

        redirect_count = redirect_info['count'] if redirect_info['error'] == None else redirect_info['error']
        log_data = {
            "Url visited": visited_url,
            "Provided Url": url,
            "Has Url changed?": visited_url != url,
            "Number of Redirects": redirect_count,
            "Status": main_http_status,
            "Provided Url Hash (in SHA-256)": url_hash,
            "Time crawled": time_crawled.strftime("%d/%m/%Y %H:%M:%S"),
            "Time taken": end_time - start_time,
            "Mouse moved when obtaining client-side data?": client_move_status,
            "Client-Side HTML script obtained?": client_html_script_status,
            "Client-side screenshot obtained?": client_screenshot_status,
        }

        output_path = os.path.join(folder_path, util_def.FILE_CRAWL_LOG_INFO)
        util.save_data_to_json_format(output_path, log_data)
