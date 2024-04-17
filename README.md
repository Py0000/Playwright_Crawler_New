# Playwright_Crawler_FYP

## Gemini Related
### Getting responses from Gemini 
* Pre-cond: Running the script from `Root` directory
* Cmd: `python3 -m baseline.gemini.gemini [mode] [type] [folder_path] [result_path]`
  * **Required** `folder_path`: (Example) datasets/validated 
  * *Optional* `mode`: ss, html or both
  * *Optional* `type`: benign or phishing
  * **Required** `folder_path`: (Example) baseline/gemini/responses


### Summarizing responses from Gemini
* Pre-cond: Running the script from `Root` directory
* Cmd: `python3 -m baseline.gemini.export_result_to_excel [shot] [mode] [folder_path] [excel_path] [hash_col] [brand_col] [cred_col] [cta_col] [cs_col] [sld_col] [pred_col] [llm_pred_col]`
  * **Required** `shot`: 0 - 3 (But only used 0 for this study)
  * *Optional* `mode`: ss, html or both
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


