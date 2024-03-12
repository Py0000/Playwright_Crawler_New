# Playwright_Crawler

## Brief Description
A web crawler designed using Playwright in Python. It is to be used for a FYP project for a comprehensive study of the chracteristics of current phishing ecosystem. 
<br>

The crawler runs on 2 main configuration: 
* Having no referrer 
* Having referrer set to its own web-domain url.
<br>

In additon to the 2 main configurations, these are the other configurations:
* User-agent: `"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"`
* User mouse movement mimicked. 
<br>

What data this crawler obtain?
* HTML script (Server-Side & Client-Side)
* Webpage Screenshot (Server-Side & Client-Side)
* TLS/SSL Certificate information of the web domain
* DNS Records information of the web domain 
* All embedded url links in the HTML script
* Network details (including detailed network information)
* Network responses data (Downloaded them from the server) 
* Client-Side scripts/requests found in the HTML script

<br>

## How to run the Crawler Script on remote VM?


### Method 1: `tmux`
1. `ssh` into the remote VM designated for this research purpose.
2. `sudo -s` to elevate to root privileges if required to change the remote VM configurations. 
3. `cd Desktop/{directory_of_interest}` to get to the path where the script is hosted.
4. Ensure all the required libraries are installed. (See `dependency.txt`)
5. Start a session using `tmux`.
6. Start the script running in the tmux session using the corresponding command
7. `Ctrl B` + `D` to detach from the tmux session.
8. Exit the ssh session if you wish to. The script will still run after exiting.

Returning to the ssh session:
1. `tmux attach -t {session_id}` to get back the existing tmux session where the script is running.




## Useful Commands

<br>

### Transfer files from Playwright_Crawler Directory (Run from local machine):
1. `scp -r sadm@fyp-0543756-i.comp.nus.edu.sg:~/Desktop/Playwright_Crawler/{date}_log_crawler.txt /mnt/f/0_App_Development_Folder/Playwright_Crawler_Dataset`
2. `scp -r sadm@fyp-0543756-i.comp.nus.edu.sg:~/Desktop/Playwright_Crawler/feeds/urls/openphish_feeds_{date}.txt /mnt/f/0_App_Development_Folder/Playwright_Crawler_Dataset`
3. `scp -r sadm@fyp-0543756-i.comp.nus.edu.sg:~/Desktop/Playwright_Crawler/dataset_{date} /mnt/f/0_App_Development_Folder/Playwright_Crawler_Dataset`


### Transfer files from Crawler_Dataset Directory (Run from local machine):
1. `scp -r sadm@fyp-0543756-i.comp.nus.edu.sg:~/Desktop/Crawler_Dataset/{date}_log_backup.txt /mnt/f/0_App_Development_Folder/Playwright_Crawler_Dataset`
2. `scp -r sadm@fyp-0543756-i.comp.nus.edu.sg:~/Desktop/Crawler_Dataset/{folder}/dataset /mnt/f/0_App_Development_Folder/Playwright_Crawler_Dataset`


### Transfer files for recrawler (Run from local machine):
1. `scp -r sadm@fyp-0543756-i.comp.nus.edu.sg:~/Desktop/Playwright_Crawler/{date}_log_recrawl.txt /mnt/f/0_App_Development_Folder/Playwright_Crawler_Dataset`
2. `scp -r sadm@fyp-0543756-i.comp.nus.edu.sg:~/Desktop/Playwright_Crawler/{date}.txt /mnt/f/0_App_Development_Folder/Playwright_Crawler_Dataset`
3. `scp -r sadm@fyp-0543756-i.comp.nus.edu.sg:~/Desktop/Playwright_Crawler/recrawl_dataset_{date} /mnt/f/0_App_Development_Folder/Playwright_Crawler_Dataset`


### Command to run crawler (From remote VM Playwright_Crawler Directory): 
1. python3 src/main_new.py {date} 2>&1 | tee {date}_log_crawler.txt


### Command to transfer data from Playwright_Crawler to Crawler_Dataset Directory (From remote VM Crawler_Dataset Directory): 
1. python3 src/automated_save_data.py {date} Phishing 2>&1 | tee {date}_log_backup.txt


### Command to run Recrawler (From remote VM Playwright_Crawler Directory):
1. python3 src/recrawler.py {date} {date}.txt 2>&1 | tee {date}_log_recrawl.txt


### Command to run VirusTotal Validator (Run from local machine):
1. python3 validator.py original_dataset_{date} {date}

### Command to run VirusTotal Revalidator (Run from local machine):
1. python3 revalidator.py url_{date}.txt {date}


### Commands for Analysis / Filtering / Baselines 
#### Finding blank pages from datasets 
* Pre-cond: Running the script `blank_page_detector.py` from `Playwright_Crawler_New` directory
* Cmd: `python3 -m analyzer.blank_page.blank_page_detector {path_to_dataset}/dataset_{date}.zip`

#### Finding duplicated files/content 
* Pre-cond: Running the script `duplicate_checker.py` from `Playwright_Crawler_New` directory
* Cmd: `python3 -m analyzer.duplicate.duplicate_checker {path_to_dataset} {type} {mode}`
  * `type`: `phishing` or `benign`
  * `mode`: `url` or `html`

#### Removing duplicated files/content 
* Pre-cond: Running the script `duplicate_remover.py` from `Playwright_Crawler_New` directory
* Cmd: `python3 -m analyzer.duplicate.duplicate_remover {duplicate_folder_txt_file_path} {mode}`
  * `mode`: `url` or `html`

#### Running llm scripts 
* Pre-cond: Running the script from `Playwright_Crawler_New` directory


  * Phishing: 
    * `file_hash_col`: B
    * `brand_col`: AA
    * `verdict_col`: Z
    * `credentials_col`: AB
    * `phishing_score_col`: AC
  * Benign
    * `file_hash_col`: B
    * `brand_col`: E
    * `verdict_col`: F
    * `credentials_col`: G
    * `phishing_score_col`: H
  * Combined
    * `file_hash_col`: B
    * `brand_col`: G
    * `verdict_col`: F
    * `credentials_col`: H
    * `phishing_score_col`: I

#### Calculating metrics 
* Pre-cond: Running the script `metrics_calc_phishing.py` or `metrics_calc_brand.py` from `Playwright_Crawler_New` directory
* Cmd: `python3 -m baseline.metrics_calc_phishing {tp} {tn} {fp} {fn}`
* Cmd: `python3 -m baseline.metrics_calc_brand {identified_correct} {identified_wrong} {indeterminate}`

#### Getting counts of data remaining (after filtering)
* Pre-cond: Running the script `counter.py` from `Playwright_Crawler_New` directory
* Cmd: `python3 -m analyzer.utils.counter {dataset_path} {type}`
  * Arg for `dataset_path`: `dataset`
  * Possible arg for `type`:
    * `blank_pages`
    * `blocked`
    * `complete`











## Useful Commands

<br>

### Running Gemini Script
* Pre-cond: Running the script from `Playwright_Crawler_New` directory
* Cmd: `python3 -m baseline.gemini.gemini_enhanced {benign or phishing} {number of examples}` 
  * `{benign or phishing}`: benign or phishing
  * `{number of examples}`: 1 to 3


#### Updating results of llm analysis to excel sheet
* Pre-cond: Running the script `export_llm_result.py` from `Playwright_Crawler_New` directory
* Cmd: `python3 -m baseline.gemini.export_llm_result {path_to_analysis_json_file} {path_to_excel_sheet} {file_hash_col} {brand_col} {credentials_col} {call_to_action_col} {confidence_score_col}`
  * `{path_to_analysis_json_file}`: `baseline/gemini/gemini_response/gemini_{date}_{shot}.json`
  * `{path_to_excel_sheet}`: `baseline/gemini/gemini_response/validation_{shot}.xlsx`
  * `file_hash_col`: 
  * `brand_col`: 
  * `credentials_col`: 
  * `call_to_action_col`: 
  * `confidence_score_col`: 


