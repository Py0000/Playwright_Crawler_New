# Playwright_Crawler_FYP

## Dataset Validation Related 
### Using VirusTotal
* Pre-cond: Running the script from `Root` directory
* Cmd: `python3 -m validation.validator [original_dataset_folder_path] [date] --is_revalidate [is_revalidate] --url_txt [url_txt]` 
  * **Required** `original_dataset_folder_path`: (Example) datasets/validated/original_dataset_251023
  * **Required** `date`: (Example) 251023
  * *Optional* `is_revalidate` yes or no
  * *Optional* `url_txt` (Example) validation/url.txt



## Filtering Related
### Filtering based on incomplete samples 
* Pre-cond: Running the script from `Root` directory
* Cmd: `python3 -m filter.faulty_data_filter [folder] [month] [date] `
  * **Required** `folder`: (Example) datasets/all
  * **Required** `month`: (Example) Oct
  * **Required** `date`: (Example) 251023


### Filtering based on response status (blocked)
* Pre-cond: Running the script from `Root` directory
* Cmd: `python3 -m filter.response_status_filter [folder] [month] [date] [phishing_mode]`
  * **Required** `folder`: (Example) datasets/all
  * **Required** `month`: (Example) Oct
  * **Required** `date`: (Example) 251023
  * **Required** `phishing_mode`: phishing or benign


### Filtering based on blank html pages 
* Pre-cond: Running the script from `Root` directory
* Cmd: `python3 -m filter.blank_page [folder] [month] [date] [phishing_mode]`
  * **Required** `folder`: (Example) datasets/all
  * **Required** `month`: (Example) Oct
  * **Required** `date`: (Example) 251023
  * **Required** `phishing_mode`: phishing or benign


### Filtering based on duplicates 
* Pre-cond: Running the script from `Root` directory
* Cmd: `python3 -m filter.duplicates [dataset_path] --phishing_mode [phishing_mode] [file_type]`
  * **Required** `folder`: (Example) datasets/all
  * *Optional* `phishing_mode`: phishing or benign
  * **Required** `file_type`: url or html


## Gemini Related
### Getting responses from Gemini (From original zip files)
* Pre-cond: Running the script from `Root` directory
* Cmd: `python3 -m baseline.gemini.gemini [mode] [phishing_mode] [folder_path] [result_path] [prompt_version]`
  * **Required** `mode`: ss, html or both
  * **Required** `phishing_mode`: phishing or benign
  * **Required** `folder_path`: (Example) datasets/validated 
  * **Required** `result_path`: (Example) baseline/gemini/responses
  * **Required** `prompt_version`: prompt sub-folder name (default is the original prompt used)

### Getting responses from Gemini (From processed normal files)
* Pre-cond: Running the script from `Root` directory
* Cmd: `python3 -m baseline.gemini.gemini_v2 [mode] [phishing_mode] [folder_path] [result_path] [prompt_version]`
  * **Required** `mode`: ss, html or both
  * **Required** `phishing_mode`: phishing or benign
  * **Required** `folder_path`: (Example) datasets/llm
  * **Required** `result_path`: (Example) baseline/gemini/responses
  * **Required** `prompt_version`: prompt sub-folder name (default is the original prompt used)

### Getting responses from GPT (From processed normal files)
* Pre-cond: Running the script from `Root` directory
* Cmd: `python3 -m baseline.gpt.gpt [mode] [phishing_mode] [folder_path] [result_path] [prompt_version]`
  * **Required** `mode`: ss, html or both
  * **Required** `phishing_mode`: phishing or benign
  * **Required** `folder_path`: (Example) datasets/llm
  * **Required** `result_path`: (Example) baseline/gpt/responses
  * **Required** `prompt_version`: prompt sub-folder name (default is the original prompt used)


### Summarizing responses from Gemini
* Pre-cond: Running the script from `Root` directory
* Cmd: `python3 -m baseline.export_results_to_excel [shot] [mode] [phishing_mode] [folder_path] [excel_path] [hash_col] [brand_col] [cred_col] [cta_col] [cs_col] [sld_col] [pred_col] [llm_pred_col]`
  * **Required** `shot`: 0 - 3 (But only used 0 for this study)
  * **Required** `mode`: ss, html or both
  * **Required** `phishing_mode`: phishing or benign
  * **Required** `folder_path`: (Example) baseline/gemini/gemini_responses/prompt_1_html_only/0-shot
  * **Required** `excel_path`: (Example) baseline/gemini/gemini_responses/prompt_1_html_only/0-shot/results_0_shot.xlsx
  * *Optional* `hash_col`: Column that stores the file hashes. Default is B
  * *Optional* `brand_col`: Column that stores the target brand. Default is F
  * *Optional* `cred_col`: Column that stores if there are any credentials. Default is G
  * *Optional* `cta_col`: Column that stores if there are any call-to-actons. Default is H
  * *Optional* `cs_col`: Column that stores the confidence score. Default is I
  * *Optional* `sld_col`: Column that stores the second level domain. Default is J
  * *Optional* `pred_col`: Column that stores the phishing prediction. Default is K
  * *Optional* `llm_pred_col`: Column that stores the phishing prediction using Gemini domain comparison. Default is L


  ### Calculating Brand Identification Metrics
  * Pre-cond: Running the script from `Root` directory
  * Cmd: `python3 -m baseline.utils.metrics_calc_identification [correct] [wrong] [indeterminate]`
    * **Required** `correct`: Number of correctly identified brands
    * **Required** `wrong`: Number of incorrectly identified brands
    * **Required** `indeterminate`: Number of brands that are unable to be identified


 ### Calculating Phishing Prediction Metrics
  * Pre-cond: Running the script from `Root` directory
  * Cmd: `python3 -m baseline.utils.metrics_calc_prediction [tp] [tn] [fp] [fn]`
    * **Required** `tp`: True Positive (Phishing predicted Phishing)
    * **Required** `tn`: True Negative (Benign predicted Benign)
    * **Required** `fp`: (Benign predicted Phishing)
    * **Required** `fn`: (Phishing predicted Benign)



## Comparative Analysis Related
### Extracting Javascript info from HTML files
  * Pre-cond: Running the script from `Root` directory
  * Cmd: `python3 -m analyzer.html_js_extractor {folder} {result_path} {phishing_mode} --ref_type {ref_type} --csr_status {csr_status}` 
    * **Required** `folder`: (Example) datasets/all
    * **Required** `result_path`: (Example) analyzer/js_info
    * **Required** `phishing_mode`: phishing or benign
    * *Optional* `ref_type`: self_ref or no_ref
    * *Optional* `csr_status`: after or before


### Analysing Browser Fingerprints
  * Pre-cond: Running the script from `Root` directory
  * Cmd: `python3 -m analyzer.browser_fingerprinting {js_info_path} {result_path} {domain_category}`
    * **Required** `js_info_path`: (Example) analyzer/js_info/no_ref_Oct or analyzer/js_info/self_ref_top10k
    * **Required** `fp_result_path`: (Example) analyzer/fingerprint_info
    * **Required** `domain_category`: (Example) Oct, Nov, Dec, top10k or 100000_105000


### Analysing Obfuscation
  * Pre-cond: Running the script from `Root` directory
  * Cmd: `python3 -m analyzer.obfuscation {js_info_path} {result_path} {domain_category}`
    * **Required** `js_info_path`: (Example) analyzer/js_info/no_ref_Oct or analyzer/js_info/self_ref_top10k
    * **Required** `fp_result_path`: (Example) analyzer/obfuscation_info
    * **Required** `domain_category`: (Example) Oct, Nov, Dec, top10k or 100000_105000  


### Analysing Certificate
  * Pre-cond: Running the script from `Root` directory
  * Cmd: `python3 -m analyzer.certificate_analysis {folder} {result_path} {phishing_mode} --ref_type {ref_type} {domain_category}`
    * **Required** `folder`: (Example) datasets/all
    * **Required** `result_path`: (Example) analyzer/certificate_info
    * **Required** `phishing_mode`: phishing or benign
    * *Optional* `ref_type`: self_ref or no_ref
    * **Required** `domain_category`: (Example) Oct, Nov, Dec, top10k or 100000_105000  
  

### Analysing DNS Records
  * Pre-cond: Running the script from `Root` directory
  * Cmd: `python3 -m analyzer.dns_analysis {folder} {result_path} {phishing_mode} --ref_type {ref_type} {domain_category}`
    * **Required** `folder`: (Example) datasets/all
    * **Required** `result_path`: (Example) analyzer/dns_info
    * **Required** `phishing_mode`: phishing or benign
    * *Optional* `ref_type`: self_ref or no_ref
    * **Required** `domain_category`: (Example) Oct, Nov, Dec, top10k or 100000_105000  
  

### Analysing Network Payloads
  * Pre-cond: Running the script from `Root` directory
  * Cmd: `python3 -m analyzer.network_analysis {folder} {result_path} {phishing_mode} {network_payload_folder} --ref_type {ref_type} {domain_category}`
    * **Required** `folder`: (Example) datasets/all
    * **Required** `result_path`: (Example) analyzer/network_info
    * **Required** `phishing_mode`: phishing or benign
    * **Required** `network_payload_folder`: network_response_files or network_data
    * *Optional* `ref_type`: self_ref or no_ref
    * **Required** `domain_category`: (Example) Oct, Nov, Dec, top10k or 100000_105000  


### Analysing HTML Payloads
  * Pre-cond: Running the script from `Root` directory
  * Cmd: `python3 -m analyzer.html_feature_analysis {folder} {result_path} {phishing_mode} --ref_type {ref_type} --csr_status {csr_status} {domain_category}`
    * **Required** `folder`: (Example) datasets/all
    * **Required** `result_path`: (Example) analyzer/network_info
    * **Required** `phishing_mode`: phishing or benign
    * *Optional* `ref_type`: self_ref or no_ref
    * *Optional* `csr_status`: after or before
    * **Required** `domain_category`: (Example) Oct, Nov, Dec, top10k or 100000_105000  