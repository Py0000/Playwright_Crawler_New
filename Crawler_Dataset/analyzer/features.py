import json
import os

import util_def

######### DEALS WITH TITLE #########
def has_title(soup):
    try: 
        if (len(soup.title.next) > 0):
            return True
        else: 
            return False
    except:
        return False


def get_title(soup):
    if (has_title(soup)):
        return soup.title.get_text()
    else:
        return "NULL"


def length_of_title(soup):
    try:
        return len(soup.title.text)
    except:
        return 0 


########## DEALS WITH FORMS & INPUTS ##########
def num_of_forms(soup):
    form_tags = soup.find_all('form')
    num = len(form_tags)

    return num


def has_forms(soup):
    return num_of_forms(soup) > 0


def form_attribute_analysis(soup):
    form_attributes = ['action', 'method', 'onsubmit', 'onreset']
    result = {
        'action': set(),
        'method': set(),
        'onsubmit': set(),
        'onreset': set(),
    }

    # Find all <form> elements
    forms = soup.find_all('form')

    for f in forms:
        # Check if the attribute exists in the form's attributes
        for attr in form_attributes:
            if attr in f.attrs:
                attribute_value = f[attr]
                result[attr].add(attribute_value)
    
    # Convert the sets into strings
    for attr in form_attributes:
        result[attr] = ', '.join(result[attr])

    return result


def num_of_forms_with_buttons(soup):
    num = 0
    forms = soup.find_all('form')

    for f in forms:
        buttons = f.find_all('button')
        if len(buttons) > 0:
            num += 1
    
    return num


def num_of_forms_with_inputs(soup):
    num = 0
    forms = soup.find_all('form')

    for f in forms:
        buttons = f.find_all('input')
        if len(buttons) > 0:
            num += 1
    
    return num


def num_of_forms_with_dropdowns(soup):
    num = 0
    forms = soup.find_all('form')

    for f in forms:
        buttons = f.find_all('select')
        if len(buttons) > 0:
            num += 1
    
    return num


def num_of_forms_with_textareas(soup):
    num = 0
    forms = soup.find_all('form')

    for f in forms:
        buttons = f.find_all('textareas')
        if len(buttons) > 0:
            num += 1
    
    return num


def num_of_textareas(soup):
    textarea_tags = soup.find_all('textarea')
    num = len(textarea_tags)

    return num 


def num_of_dropdowns(soup):
    tags = soup.find_all('select')
    num = len(tags)

    return num 


def num_of_inputs(soup):
    input_tags = soup.find_all('input')
    num = len(input_tags)

    return num


def has_inputs(soup):
    return num_of_inputs(soup) > 0


def input_attributes_analysis(soup):
    input_attributes = ['type', 'name', 'submit', 'placeholder']
    result = {
        'type': set(),
        'name': set(),
        'submit': set(),
        'placeholder': set(),
    }

    inputs = soup.find_all('input')

    for i in inputs:
        for attr in input_attributes:
            if attr in i.attrs:
                attribute_value = i[attr]
                result[attr].add(attribute_value)

    # Convert the sets into strings
    for attr in input_attributes:
        result[attr] = ', '.join(result[attr])
    
    return result


# Can be created using the <button> element 
# Or the <input> element with the type attribute set to "button"
def num_of_buttons(soup):
    # Find all <button> elements
    button_tags = soup.find_all('button')  

    # Find <input> elements with type="button"
    input_buttons = soup.find_all('input', {'type': 'button'})

    num = len(button_tags) + len(input_buttons)

    return num


def has_buttons(soup):
    return num_of_buttons(soup) > 0


def button_attributes_analysis(soup):
    attributes = ['type', 'onclick']

    result = {
        'type': set(),
        'onclick': set()
    }

    buttons = soup.find_all('button')
    input_buttons = soup.find_all('input', {'type': 'button'})

    for b in buttons:
        for attr in attributes:
            if attr in b.attrs:
                attribute_value = b[attr]
                result[attr].add(attribute_value)

    # Convert the sets into strings
    for attr in attributes:
        result[attr] = ', '.join(result[attr])

    return result

def num_of_outputs(soup):
    tags = soup.find_all('output')
    num = len(tags)

    return num 


########## DEALS WITH LINKS ##########
def num_of_anchor_url(soup):
    num = len(soup.find_all('a', href=True))
    return num

# More of a double-check function
def num_of_anchor_url_with_http(soup):
    count = 0
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and href.startswith(('http://', 'https://')):
            count += 1
    
    return count

# More of a double-check function
def num_of_a_tags(soup):
    return len(soup.find_all('a'))



########## DEALS WITH FRAMES ##########
def num_of_iframes(soup):
    return len(soup.find_all("iframe"))


# width, height and frameborder attribute are all 0
def num_of_invisible_iframes(soup):
    iframes = soup.find_all('iframe')
    count = 0
    for iframe in iframes:
        hasNoWidth = iframe.get('width') == '0'
        hasNoHeight = iframe.get('height') == '0'
        hasNoFrameBorder = iframe.get('frameborder') == '0'
        if (hasNoWidth and hasNoHeight and hasNoFrameBorder):
            count += 1
    
    return count

# atleast one of (width, height, frameborder) is 0
def num_of_semi_invisible_iframes(soup):
    iframes = soup.find_all('iframe')
    count = 0
    for iframe in iframes:
        hasNoWidth = iframe.get('width') == '0'
        hasNoHeight = iframe.get('height') == '0'
        hasNoFrameBorder = iframe.get('frameborder') == '0'
        if (hasNoWidth or hasNoHeight or hasNoFrameBorder):
            count += 1
    
    return count

# Check function
def num_of_visible_iframes(soup):
    iframes = soup.find_all('iframe')
    count = 0
    for iframe in iframes:
        hasWidth = iframe.get('width') != '0'
        hasHeight = iframe.get('height') != '0'
        hasFrameBorder = iframe.get('frameborder') != '0'
        if (hasWidth and hasHeight and hasFrameBorder):
            count += 1
    
    return count

# Get an external re-direction link that is present in the iframe if any
def iframe_src_analysis(soup):
    iframes = soup.find_all('iframe')
    src_attributes = []
    for iframe in iframes:
        src = iframe.get('src')
        if src:
            src_attributes.append(src)
    
    return src_attributes


########## DEALS WITH STYLES & STYLESHEETS ##########

# Returns the number of css  present in the HTML Script
# Searches for <link> tags with the rel attribute set to "stylesheet"
def num_of_stylesheets_total(soup):
    link_tags = soup.find_all('link', rel='stylesheet')
    num = len(link_tags) 

    return num

def has_stylesheets(soup):
    return num_of_stylesheets_total(soup) > 0

# Returns the number of css  present in the HTML Script
# Searches for <link> tags with the rel attribute set to "stylesheet", type attribute set to "text/css" 
def num_of_css_stylesheets(soup):
    # Search for <link> tags with rel="stylesheet" and type="text/css"
    link_tags = soup.find_all('link', rel='stylesheet', type='text/css')

    num_css = len(link_tags) 

    return num_css

def has_css_stylesheets(soup):
    return num_of_css_stylesheets(soup) > 0


# Returns number of non-css stylesheets present
# Searches for <link> tags with the rel attribute set to "stylesheet" but excludes those with type attribute set to "text/css" 
def num_of_non_css_stylesheets(soup):
    # Search for <link> tags with rel="stylesheet"
    link_tags = soup.find_all('link', rel='stylesheet')

    # Count the number of non-CSS stylesheets
    non_css_count = 0

    for tag in link_tags:
        if 'type' in tag.attrs and tag['type'].lower() != 'text/css':
            non_css_count += 1

    return non_css_count


def has_non_css_stylesheets(soup):
    return num_of_non_css_stylesheets(soup) > 0


# Returns the number of stylesheet present in the HTML Script
# Searches <style> tags
def num_of_internal_styles(soup):
    # Search for <style> tags
    style_tags = soup.find_all('style')

    # Count the number of styles
    num_of_styles = len(style_tags)

    return num_of_styles


def num_of_inline_styles(soup):
    num = len(soup.find_all("span"))
    return num


def num_of_hr(soup):
    num = len(soup.find_all("hr"))
    return num


def num_of_hr_with_style(soup):
    hr_elements = soup.find_all('hr')
    count = 0

    for hr in hr_elements:
        if hr.get('style'):
            count += 1

    return count




########### DEALS WITH RS BETWEEN HTML SCRIPT & OTHER RESOURCE ##########
def num_of_links(soup):
    return len(soup.find_all("link"))

def num_of_icon_rs(soup):
    return len(soup.find_all("link", rel='icon'))

def num_of_common_link_attrs(soup):
    stylesheets = len(soup.find_all('link', rel='stylesheet'))
    icons = len(soup.find_all("link", rel='icon'))
    preconnects = len(soup.find_all("link", rel='preconnect'))
    alternates = len(soup.find_all("link", rel='alternate'))

    num = stylesheets + icons + preconnects + alternates
    return num

def link_analysis(soup):
    result = []
    link_tags = soup.find_all("link")

    for link in link_tags:
        rel = link.get('rel')
        if rel is not None:
            result.append(rel)

    # Flatten the nested rel list obtained in the loop
    flattened_result = [item for sublist in result for item in sublist]
    return flattened_result    


def num_of_navs(soup):
    num = len(soup.find_all("nav"))
    return num



########## DEALS WITH PROGRAMMING ##########
def num_of_scripts(soup):
    num = len(soup.find_all("script"))
    return num


def num_of_inline_js_scripts(soup):
    script_elements = soup.find_all('script')
    count = 0

    for script in script_elements:
        if not script.has_attr('src'):
            count += 1

    return count


def num_of_external_scripts(soup):
    script_elements = soup.find_all('script')
    count = 0

    for script in script_elements:
        if script.has_attr('src'):
            count += 1

    return count


def num_of_async_scripts(soup):
    script_elements = soup.find_all('script')
    count = 0

    for script in script_elements:
        if script.has_attr('async') or script.get('async') == '':
            count += 1

    return count


def num_of_defer_scripts(soup):
    script_elements = soup.find_all('script')
    count = 0

    for script in script_elements:
        if script.has_attr('defer') or script.get('defer') == '':
            count += 1

    return count


def external_script_analysis(soup):
    script_elements = soup.find_all('script')
    src_values = []

    for script in script_elements:
        src = script.get('src')
        if src:
            src_values.append(src)

    return src_values


def num_of_noscripts(soup):
    num = len(soup.find_all("noscript"))
    return num


def num_of_embeds(soup):
    num = len(soup.find_all("embed"))
    return num


def embed_src_analysis(soup):
    embed_elements = soup.find_all('embed')
    src_values = []

    for embed in embed_elements:
        src = embed.get('src')
        if src:
            src_values.append(src)
    
    return src_values


def embed_type_analysis(soup):
    embed_elements = soup.find_all('embed')
    type_values = []

    for embed in embed_elements:
        src = embed.get('type')
        if src:
            type_values.append(src)
    
    return type_values


def num_of_objects(soup):
    num = len(soup.find_all("object"))
    return num


def object_data_analysis(soup):
    obj_elements = soup.find_all('object')
    data_values = []

    for obj in obj_elements:
        data = obj.get('data')
        if data:
            data_values.append(data)
    
    return data_values


def object_type_analysis(soup):
    obj_elements = soup.find_all('object')
    type_values = []

    for obj in obj_elements:
        src = obj.get('type')
        if src:
            type_values.append(src)
    
    return type_values


def num_of_codes(soup):
    num = len(soup.find_all("code"))
    return num


########## DEALS WITH MEDIA AND GRAPHICS #########
def num_of_imgs(soup):
    num = len(soup.find_all("img"))
    return num

def num_of_videos(soup):
    num = len(soup.find_all("video"))
    return num

def num_of_audios(soup):
    num = len(soup.find_all("audio"))
    return num

def num_of_svgs(soup):
    num = len(soup.find_all("svg"))
    return num

def num_of_other_source_svgs(soup):
    # Find the number of referenced SVG files using <img> or <object> tag
    img_svgs = soup.find_all('img[src$=".svg"]')  # Find <img> elements with .svg extension
    object_svgs = soup.find_all('object[type="image/svg+xml"]')  # Find <object> elements with type="image/svg+xml"
    num = len(img_svgs) + len(object_svgs)

    return num

def num_of_pictures(soup):
    num = len(soup.find_all("picture"))
    return num

def num_of_clickable_image_maps(soup):
    num = len(soup.find_all("map"))
    return num

def num_of_canvas(soup):
    num = len(soup.find_all("canvas"))
    return num

def num_of_sources(soup):
    num = len(soup.find_all("source"))
    return num

def num_of_tracks(soup):
    num = len(soup.find_all("track"))
    return num




########## DEALS WITH LISTS ##########
def num_of_unordered_list(soup):
    num = len(soup.find_all("ul"))
    return num


def num_of_ordered_list(soup):
    num = len(soup.find_all("ol"))
    return num


def num_of_description_list(soup):
    num = len(soup.find_all("dl"))
    return num


def num_of_dt(soup):
    num = len(soup.find_all("dt"))
    return num

def num_of_dd(soup):
    num = len(soup.find_all("dd"))
    return num

def num_of_exceptional_dt(soup):
    dt_elements = soup.find_all('dt')
    count = 0
    for dt in dt_elements:
        if not dt.find_parent('dl'):
            count += 1
    
    return count

def num_of_normal_dt(soup):
    dt_elements = soup.find_all('dt')
    count = 0
    for dt in dt_elements:
        if dt.find_parent('dl'):
            count += 1
    
    return count

def num_of_exceptional_dd(soup):
    dd_elements = soup.find_all('dd')
    count = 0
    for dd in dd_elements:
        if not dd.find_parent('dl'):
            count += 1
    
    return count

def num_of_normal_dd(soup):
    dd_elements = soup.find_all('dd')
    count = 0
    for dd in dd_elements:
        if dd.find_parent('dl'):
            count += 1
    
    return count


########## DEALS WITH TABLE ##########
def num_of_tables(soup):
    num = len(soup.find_all("table"))
    return num



########### LENGTH OF HTML SCRIPT TEXTS #########
def length_of_text(soup):
    return len(soup.get_text())




########## DEALS WITH BASIC HTML INFO ###########
def num_of_head(soup):
    num = len(soup.find_all('head'))
    return num


def num_of_body(soup):
    num = len(soup.find_all('body'))
    return num


def num_of_h1(soup):
    num = len(soup.find_all('h1'))
    return num


def num_of_h2(soup):
    num = len(soup.find_all('h2'))
    return num


def num_of_h3(soup):
    num = len(soup.find_all('h3'))
    return num


def num_of_h4(soup):
    num = len(soup.find_all('h4'))
    return num


def num_of_h5(soup):
    num = len(soup.find_all('h5'))
    return num


def num_of_h6(soup):
    num = len(soup.find_all('h6'))
    return num


def num_of_p(soup):
    num = len(soup.find_all('p'))
    return num


def num_of_bases(soup):
    num = len(soup.find_all("base"))
    return num


def has_exceptional_bases(soup):
    base_tags = soup.find_all('base')
    for base in base_tags:
        if base.parent.name != 'head':
            return False
    return True



########## DEALS WITH META INFO ##########
def num_of_metas(soup):
    num = len(soup.find_all("meta"))
    return num

def num_of_meta_with_refresh_attrs(soup):
    num = soup.find_all('meta', attrs={'http-equiv': 'refresh'})
    return len(num)

def meta_refresh_analysis(soup):
    meta_tags = soup.find_all('meta', attrs={'http-equiv': 'refresh'})
    content_values = [meta.get('content') for meta in meta_tags]
    result_string = ""
    for content in content_values:
        if content == None:
            continue
        result_string = '\n'.join(content) 
    return result_string    




########## DEALS WITH SEMENATICS ##########
def num_of_divs(soup):
    num = len(soup.find_all("div"))
    return num


def num_of_headers(soup):
    num = len(soup.find_all("header"))
    return num


def num_of_footers(soup):
    num = len(soup.find_all("footer"))
    return num


def num_of_mains(soup):
    num = len(soup.find_all("main"))
    return num


def num_of_sections(soup):
    num = len(soup.find_all("section"))
    return num


def num_of_articles(soup):
    num = len(soup.find_all("article"))
    return num


def num_of_asides(soup):
    num = len(soup.find_all("aside"))
    return num


def num_of_details(soup):
    num = len(soup.find_all("detail"))
    return num


def num_of_dialogs(soup):
    num = len(soup.find_all("dialog"))
    return num

def num_of_machine_readable_datas(soup):
    num = len(soup.find_all("data"))
    return num



######### DEALS WITH FORMATTING ##########
def num_of_formatting_tags(soup):
    abbr_elements = len(soup.find_all('abbr'))
    b_elements = len(soup.find_all('b'))
    bdi_elements = len(soup.find_all('bdi'))
    bdo_elements = len(soup.find_all('bdo'))
    blockquote_elements = len(soup.find_all('blockquote'))
    cite_elements = len(soup.find_all('cite'))
    del_elements = len(soup.find_all('del'))
    dfn_elements = len(soup.find_all('dfn'))
    em_elements = len(soup.find_all('em'))
    i_elements = len(soup.find_all('i'))
    ins_elements = len(soup.find_all('ins'))
    kbd_elements = len(soup.find_all('kbd'))
    mark_elements = len(soup.find_all('mark'))
    pre_elements = len(soup.find_all('pre'))
    q_elements = len(soup.find_all('q'))
    s_elements = len(soup.find_all('s'))
    small_elements = len(soup.find_all('small'))
    samp_elements = len(soup.find_all('samp'))
    strong_elements = len(soup.find_all('strong'))
    sup_elements = len(soup.find_all('sup'))
    sub_elements = len(soup.find_all('sub'))
    u_elements = len(soup.find_all('u'))
    var_element = len(soup.find_all('var'))

    count = abbr_elements + b_elements + bdi_elements + bdo_elements + blockquote_elements + cite_elements + del_elements 
    + dfn_elements + em_elements + i_elements + ins_elements + kbd_elements + mark_elements + pre_elements + q_elements 
    + s_elements + small_elements + samp_elements + strong_elements + sup_elements + sub_elements + u_elements + var_element 

    return count


def has_formatting_tags(soup):
    return num_of_formatting_tags(soup) > 0


def num_of_progess_meter_elements(soup):
    meter_elements = len(soup.find_all('meter'))
    progress_elements = len(soup.find_all('progress'))

    return meter_elements + progress_elements


def num_of_templates(soup):
    num = len(soup.find_all("template"))
    return num  



########## Less important stuff ###########
def num_of_br(soup):
    num = len(soup.find_all("br"))
    return num


def has_html_tag(soup):
    return soup.html is not None


########## DEALS WITH TAGS ##########
def get_unique_tags(folder_path, file_name, is_aft_flag):
    file_path = os.path.join(os.getcwd(), folder_path, file_name)
    indicator = util_def.AFTER_CLIENT_SIDE_RENDERING_INDICATOR if is_aft_flag else util_def.BEFORE_CLIENT_SIDE_RENDERING_INDICATOR
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        parsed_data = json.loads(content)
        html_tag = parsed_data[indicator]
        
        elements = html_tag.replace('{', '').replace('}', '').replace('\'', '').split(', ')
    except Exception as e:
        print(f"Error reading file: {file_name} in {folder_path} for {indicator}\nError is: {e}")
        elements = ""
        pass

    return elements