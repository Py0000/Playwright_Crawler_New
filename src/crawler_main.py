import asyncio
import os 
import time

from bs4 import BeautifulSoup
from datetime import datetime
from playwright.async_api import async_playwright

import crawler_actions
import crawler_certificate_extractor as certificate_extractor
import crawler_dns_extractor as dns_extractor
import crawler_utilities
import util
import util_def 

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


# Obtains the server-side data for the webpage
# Data retrieves includes: Page Screenshot, Page HTML Script
async def get_server_side_data(browser, ref_flag, folder_path, to_visit_url):
    # Intercept network requests
    async def block_external_resources_request(route, request):
        if request.resource_type != "document":
            await route.abort()
        else:
            await route.continue_()
    
    print("Getting server-side data...")
    try:
        context = await browser.new_context(java_script_enabled=False)
        page = await context.new_page()
        await set_page_referrer(page, ref_flag, to_visit_url)
        print("[Server-Side] Context & Page setup done...")

        # Ensure that the routing function is applied to all requests
        print("[Server-Side] Visiting url...")
        await page.route('**/*', block_external_resources_request)
        await page.goto(to_visit_url)

        print("[Server-Side] Executing user action...")
        server_move_status = await crawler_actions.execute_user_action(page)

        print("[Server-Side] Waiting for page to load...")
        await wait_for_page_to_load(page)

        print("[Server-Side] Saving screenshot...")
        server_screenshot_status = await crawler_utilities.save_screenshot(page, folder_path, util_def.FILE_SCREENSHOT_BEF)
        
        print("[Server-Side] Saving HTML script...")
        server_html_script = await page.content()
        soup = BeautifulSoup(server_html_script, "lxml")
        crawler_utilities.save_html_script(folder_path, util_def.FILE_HTML_SCRIPT_BEF, soup.prettify())
        status = "Success"

    except Exception as e:
        crawler_utilities.save_html_script(
            folder_path, util_def.FILE_HTML_SCRIPT_BEF, f"[Server-Side] Error occurred for url: {to_visit_url}\n{e}"
        )
        status = "Error visiting page"
        server_move_status = "Error visiting page"
        server_screenshot_status = "Error visiting page"
        #server_html_tag = "Error visiting page"

    finally:
        if page:
            print("[Server-Side: finally block] Closing page...")
            await page.close()
        if context:
            print("[Server-Side: finally block] Closing context...")
            await context.close()
        
        print("Server-side Data Done...")
        return status, server_move_status, server_screenshot_status


# Obtains all the client-side calls that is present in the page HTML Script
async def get_client_side_script(page, folder_path):
    try:
        client_side_scripts = await page.evaluate(crawler_utilities.client_side_scripts_injection_code)

        # Format client-side scripts for better readability
        # Create a dictionary to store the client-side script data
        script_data = {}
        for index, script in enumerate(client_side_scripts):
            script_data[f'script_{index + 1}'] = script
        
        # Save data to a JSON file
        crawler_utilities.save_client_side_script(folder_path, script_data)
        status = "Success"
    except:
        status = "Failed"
    finally:
        return status


def obtain_certificate_info(visited_url, folder_path):
    try:
        # Obtains the TLS/SSL certificate info for the page
        cert_extraction_status = certificate_extractor.extract_certificate_info(visited_url, folder_path)
    except:
        cert_extraction_status = "Error retrieving certificate info"
    finally:
        return cert_extraction_status
        

def obtain_dns_records_info(visited_url, folder_path):
    try:
        # Obtains the DNS records info for the page
        dns_extraction_status = dns_extractor.extract_dns_records(visited_url, folder_path)
    except:
        dns_extraction_status = "Error retrieving dns info"
    finally:
        return dns_extraction_status        


# dataset_folder_name: refers to the name of the (base)folder to store the crawled data
async def crawl(browser, url, url_hash, folder_path, timeout_multiplier, ref_flag):
    timeout_limit = 10 * timeout_multiplier
    start_time = time.time()
    time_crawled = datetime.now()

    # Setup folders and paths required for data storage 
    util.generate_network_folders(folder_path)
    har_network_path = os.path.join(folder_path, util_def.FOLDER_NETWORK_FRAGMENTS ,util_def.FILE_NETWORK_HAR)

    try:
        # Obtains the server-side view of the HTML Script and page screenshot 
        server_html_status, server_move_status, server_screenshot_status = await timeout_wrapper(
            get_server_side_data,
            browser, ref_flag, folder_path, url,
            timeout=timeout_limit,
            default_values=("Timeout", "Timeout", "Timeout", "Timeout")
        )
    except Exception as e:
        print("Error obtaining server-side data: ", e)

    try:
        context = await browser.new_context(record_har_path=har_network_path, record_har_content="attach")
        page = await context.new_page()
        await set_page_referrer(page, ref_flag, url)
        
        main_http_status = "Not Visited"
        timeout_task = None
        print("[Client-Side] Context & Page setup done...")

        # Global variable to track the last request time
        last_request_data = {"timestamp": None}
        network_event = asyncio.Event()

        # Listt o hold network resquest made when visiting the page.
        captured_events = []

        # To capture number of redirection of url that occurred
        redirect_info = {
            'count': 0,
            'error': None
        }

        def on_response(response):
            nonlocal redirect_count
            if 300 <= response.status < 400:
                redirect_info['count'] += 1
        
        # Function to capture and store all network requests made.
        async def capture_request(payload):
            captured_event = payload
            captured_events.append(captured_event)
            last_request_data["timestamp"] = datetime.now()
            network_event.set()
        
        async def check_for_timeout():
            try:
                await asyncio.wait_for(network_event.wait(), timeout=5)
            except asyncio.TimeoutError:
                print("No network requests for 5s, proceeding...")
            finally:
                network_event.clear()  # Reset the event for potential future use
        
        client = await page.context.new_cdp_session(page) # Utilize CDP to capture network requests.
        await client.send("Network.enable")
        client.on("Network.requestWillBeSent", capture_request)
        timeout_task = asyncio.create_task(check_for_timeout())
        print("[Client-Side] Network Interception Setup Done...")

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

        print("[Client-Side] Extracting inline client-side script...")
        client_client_side_script_status = await timeout_wrapper(
            get_client_side_script, 
            page, folder_path, 
            timeout=timeout_limit, 
            default_values="Timeout"
        )


        print("[Client-Side] Saving HTML script...")
        content = soup.prettify()
        if content is not None:
            crawler_utilities.save_html_script(folder_path, util_def.FILE_HTML_SCRIPT_AFT, content)
            await crawler_utilities.extract_links(folder_path, soup, page, visited_url)
        
        client_html_script_status = "Success"

        print("[Client-Side] Saving Network data...")
        detailed_network_status = crawler_utilities.save_more_detailed_network_logs(folder_path, captured_events)
        
        print("[Client-Side] Extracting Certificate data...")
        cert_extraction_status = obtain_certificate_info(visited_url, folder_path)

        print("[Client-Side] Extracting DNS data...")
        dns_extraction_status = obtain_dns_records_info(visited_url, folder_path)

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
        crawler_utilities.save_html_script(folder_path, util_def.FILE_HTML_SCRIPT_AFT, f"Error occurred for url: {url}\n{e}")
        client_html_script_status = "Failed"

        visited_url = url
        server_move_status = ERROR_MSG
        server_html_status = ERROR_MSG
        server_screenshot_status = ERROR_MSG
        dns_extraction_status = ERROR_MSG
        cert_extraction_status = ERROR_MSG
        client_move_status = ERROR_MSG
        client_html_script_status = ERROR_MSG
        client_screenshot_status = ERROR_MSG
        client_client_side_script_status = ERROR_MSG
        detailed_network_status = ERROR_MSG
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
            "Certificate Extraction": cert_extraction_status,
            "DNS Records Extraction": dns_extraction_status,
            "Mouse moved when obtaining server-side data?": server_move_status,
            "Server-Side HTML script obtained?": server_html_status,
            "Server-side screenshot obtained?": server_screenshot_status,
            "Mouse moved when obtaining client-side data?": client_move_status,
            "Client-Side HTML script obtained?": client_html_script_status,
            "Client-side screenshot obtained?": client_screenshot_status,
            "Client-Side scripts obtained?":  client_client_side_script_status,
            "Network data saved?": detailed_network_status
        }

        output_path = os.path.join(folder_path, util_def.FILE_CRAWL_LOG_INFO)
        util.save_data_to_json_format(output_path, log_data)
