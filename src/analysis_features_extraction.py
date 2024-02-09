import os
import json
import pandas as pd
from bs4 import BeautifulSoup

import features as fe
import util_def
import util


DATAFRAME_COLUMNS = [
        "Webpage Title",
        "Link",
        "Has forms?",
        "Num of forms",
        "Num of forms with buttons",
        "Num of forms with inputs",
        "Num of forms with dropdowns",
        "Num of forms with textareas",
        "Num of dropdowns",
        "Num of textareas",
        "Has inputs?",
        "Num of inputs",
        "Has buttons?",
        "Num of buttons",
        "Num of outputs",
        "Num of anchor urls",
        "Num of anchor urls with http/https",
        "Num of <a> tags",
        "Num of iframes",
        "Num of invisible iframes",
        "Num of semi-invisible iframes",
        "Num of visibile iframes",
        "Has stylesheets?",
        "Has css stylesheets?",
        "Has non-css stylesheets?",
        "Num of stylesheets",
        "Num of css stylesheets",
        "Num of non-css stylesheets",
        "Num of internal styles (<style>)",
        "Num of inline styles (<span>)",
        "Num of thematic change in content <hr>",
        "Num of <hr> with styles",
        "Num of <link> tags",
        "Num of icons (in <link>)",
        "Num of common attrs for <link>\n(stylesheet, icon, preconnect, alternate)",
        "Num of scripts",
        "Num of inline JS scripts",
        "Num of external scripts",
        "Num of async scripts",
        "Num of defer scripts",
        "Num of noscripts\n(fallback when JS is not available/supported)",
        "Num of embed external contents",
        "Num of object external contents",
        "Num of <nav> tags",
        "Num of images",
        "Num of videos",
        "Num of audios",
        "Num of pictures",
        "Num of clickable image maps",
        "Num of svgs",
        "Num of referrenced svgs (in <img> or <object>)",
        "Num of canvas",
        "Num of sources (within <video>, <audio>)",
        "Num of tracks (within <video>)",
        "Num of unordered list",
        "Num of ordered list",
        "Num of description list",
        "Num of description text (dt)",
        "Num of normal <dt>", 
        "Num of exceptional <dt>", 
        "Num of description desc (dd)",
        "Num of normal <dd>", 
        "Num of exceptional <dd>", 
        "Num of tables",
        "Num of heads",
        "Num of body",
        "Num of h1",
        "Num of h2",
        "Num of h3",
        "Num of h4",
        "Num of h5",
        "Num of h6",
        "Num of metas",
        "Meta Refresh analysis",
        "Num of <p> tags",
        "Num of bases",
        "Has exceptional bases\n(Not supposed to)",
        "Num of divs",
        "Num of headers",
        "Num of footers",
        "Num of mains",
        "Num of sections",
        "Num of articles",
        "Num of asides",
        "Num of details",
        "Num of dialogs",
        "Num of machine-readable data (<data>)",
        "Length of Webpage Title",
        "Length of texts in HTML Script",
        "Num of Templates",
        "Has Formatting Tags",
        "Num of Formatting Tags",
        "Num of <progress> and <meter> tags",
        "Has <html> tag",
        "Num of <br>",
    ]


def create_df_for_each_url(output_folder, df, is_aft_flag):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    output_filename = util_def.EXCEL_FEATURES_AFT if is_aft_flag else util_def.EXCEL_FEATURES_BEF
    output_path = os.path.join(output_folder, output_filename)
    df.to_excel(output_path, index=False)


def create_json_for_each_url(soup, url, dataset_folder_name, output_folder_name, is_aft_flag):
    if not os.path.exists(output_folder_name):
        os.makedirs(output_folder_name)

    tag_file_name = util_def.FILE_HTML_TAG
    result = {}

    result["Referenced HTML file"] = dataset_folder_name
    result["URL"] = url 
    result["Page Title"] = fe.get_title(soup).strip() if (len(fe.get_title(soup)) > 0) else ""
    
    result["Form Attributes"] = fe.form_attribute_analysis(soup)
    result["Input Attributes"] = fe.input_attributes_analysis(soup)
    result["Button Attributes"] = fe.button_attributes_analysis(soup)
    result["Iframe Src Attributes"] = fe.iframe_src_analysis(soup)
    result["Link Attributes"] = fe.link_analysis(soup)
    result["External Script Attributes"] = fe.external_script_analysis(soup)
    result["Embed Type"] = fe.embed_type_analysis(soup)
    result["Embed Src"] = fe.embed_src_analysis(soup)
    result["Object Type"] = fe.object_type_analysis(soup)
    result["Object Data"] = fe.object_data_analysis(soup)
    result["Meta Refresh Attributes"] = fe.meta_refresh_analysis(soup)
    result["Unique Tags"] = fe.get_unique_tags(dataset_folder_name, tag_file_name, is_aft_flag)

    output_filename = util_def.JSON_FEATURES_AFT if is_aft_flag else util_def.JSON_FEATURES_BEF
    with open(os.path.join(output_folder_name, output_filename), 'w') as file:
        json.dump(result, file, indent=4)
    

# Step 1: Define a function that opens a html file and returns the content
def open_file(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        return f.read()


# Step 2: Define a function that creates a BeautifulSoup object
def create_soup(text):
    return BeautifulSoup(text, "lxml")


# Step 3: Define a function that creates a vector by running all feature functions for the soup object
def create_vector(soup, url):
    return [
        fe.get_title(soup),
        url,
        fe.has_forms(soup),
        fe.num_of_forms(soup),
        fe.num_of_forms_with_buttons(soup),
        fe.num_of_forms_with_inputs(soup),
        fe.num_of_forms_with_dropdowns(soup),
        fe.num_of_forms_with_textareas(soup),
        fe.num_of_dropdowns(soup),
        fe.num_of_textareas(soup),
        fe.has_inputs(soup),
        fe.num_of_inputs(soup),
        fe.has_buttons(soup),
        fe.num_of_buttons(soup),
        fe.num_of_outputs(soup),
        fe.num_of_anchor_url(soup),
        fe.num_of_anchor_url_with_http(soup),
        fe.num_of_a_tags(soup),
        fe.num_of_iframes(soup),
        fe.num_of_invisible_iframes(soup),
        fe.num_of_semi_invisible_iframes(soup),
        fe.num_of_visible_iframes(soup),
        fe.has_stylesheets(soup),
        fe.has_css_stylesheets(soup),
        fe.has_non_css_stylesheets(soup),
        fe.num_of_stylesheets_total(soup),
        fe.num_of_css_stylesheets(soup),
        fe.num_of_non_css_stylesheets(soup),
        fe.num_of_internal_styles(soup),
        fe.num_of_inline_styles(soup),
        fe.num_of_hr(soup),
        fe.num_of_hr_with_style(soup),
        fe.num_of_links(soup),
        fe.num_of_icon_rs(soup),
        fe.num_of_common_link_attrs(soup),
        fe.num_of_scripts(soup),
        fe.num_of_inline_js_scripts(soup),
        fe.num_of_external_scripts(soup),
        fe.num_of_async_scripts(soup),
        fe.num_of_defer_scripts(soup),
        fe.num_of_noscripts(soup),
        fe.num_of_embeds(soup),
        fe.num_of_objects(soup),
        fe.num_of_navs(soup),
        fe.num_of_imgs(soup),
        fe.num_of_videos(soup),
        fe.num_of_audios(soup),
        fe.num_of_pictures(soup),
        fe.num_of_clickable_image_maps(soup),
        fe.num_of_svgs(soup),
        fe.num_of_other_source_svgs(soup),
        fe.num_of_canvas(soup),
        fe.num_of_sources(soup),
        fe.num_of_tracks(soup),
        fe.num_of_unordered_list(soup),
        fe.num_of_ordered_list(soup),
        fe.num_of_description_list(soup),
        fe.num_of_dt(soup),
        fe.num_of_normal_dt(soup),
        fe.num_of_exceptional_dt(soup),
        fe.num_of_dd(soup),
        fe.num_of_normal_dd(soup),
        fe.num_of_exceptional_dd(soup),
        fe.num_of_tables(soup),
        fe.num_of_head(soup),
        fe.num_of_body(soup),
        fe.num_of_h1(soup),
        fe.num_of_h2(soup),
        fe.num_of_h3(soup),
        fe.num_of_h4(soup),
        fe.num_of_h5(soup),
        fe.num_of_h6(soup),
        fe.num_of_metas(soup),
        fe.num_of_meta_with_refresh_attrs(soup),
        fe.num_of_p(soup),
        fe.num_of_bases(soup),
        fe.has_exceptional_bases(soup),
        fe.num_of_divs(soup),
        fe.num_of_headers(soup),
        fe.num_of_footers(soup),
        fe.num_of_mains(soup),
        fe.num_of_sections(soup),
        fe.num_of_articles(soup),
        fe.num_of_asides(soup),
        fe.num_of_details(soup),
        fe.num_of_dialogs(soup),
        fe.num_of_machine_readable_datas(soup),
        fe.length_of_title(soup),
        fe.length_of_text(soup),
        fe.num_of_templates(soup),
        fe.has_formatting_tags(soup),
        fe.num_of_formatting_tags(soup),
        fe.num_of_progess_meter_elements(soup),
        fe.has_html_tag(soup),
        fe.num_of_br(soup),
    ]


# Creates a consolidated df in excel format for the html tags for each url.
# In the process, it also generates individual excel and json data for each url.
def create_dataframe(ref_specific_dataset_path, ref_specific_analyzed_data_path, is_aft_flag):
    sub_folders = [d for d in os.listdir(ref_specific_dataset_path) if os.path.isdir(os.path.join(ref_specific_dataset_path, d))]

    html_file_name = util_def.FILE_HTML_SCRIPT_AFT if is_aft_flag else util_def.FILE_HTML_SCRIPT_BEF

    df = pd.DataFrame()

    for sub_folder in sub_folders:
        # Retrieves the webpage url information form log files
        url_info_filepath = os.path.join(ref_specific_dataset_path, sub_folder, util_def.FILE_CRAWL_LOG_INFO)
        url = ""
        if os.path.exists(url_info_filepath):
            with open(url_info_filepath, "r") as f:
                url_data = f.read()
            parsed_json_data = json.loads(url_data)
            url = parsed_json_data["Provided Url"]

        # retrieve the html script 
        html_filepath = os.path.join(ref_specific_dataset_path, sub_folder, html_file_name)
        if os.path.exists(html_filepath):
            soup = create_soup(open_file(html_filepath))
            data = [create_vector(soup, url)]
        
        # Generates excel for the current url as well as json
        current_df = pd.DataFrame(data=data, columns=DATAFRAME_COLUMNS)
        output_path = os.path.join(ref_specific_analyzed_data_path, sub_folder)
        create_df_for_each_url(output_path, df, is_aft_flag)
        create_json_for_each_url(soup, url, os.path.join(ref_specific_dataset_path, sub_folder), output_path, is_aft_flag)

        # combine each url data together
        df = pd.concat([df, current_df], ignore_index=True)
    
    # Generates the consoldiated excel 
    output_filename = util_def.EXCEL_FEATURES_CONSOLIDATED_AFT if is_aft_flag else util_def.EXCEL_FEATURES_CONSOLIDATED_BEF
    output_path = os.path.join(ref_specific_analyzed_data_path, output_filename)
    df.to_excel(output_path, index=False)



def extract_features(ref_specific_dataset_path, ref_specific_analyzed_data_path):
    create_dataframe(ref_specific_dataset_path, ref_specific_analyzed_data_path, is_aft_flag=True)
    create_dataframe(ref_specific_dataset_path, ref_specific_analyzed_data_path, is_aft_flag=False)
    