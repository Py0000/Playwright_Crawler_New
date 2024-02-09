from urllib.parse import urlparse
import tldextract



#--------------------------------- Deals with title ---------------------------------
def has_title(soup):
    try: 
        return len(soup.title.next) > 0
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


def is_url_domain_in_title(soup, url):
    domain = tldextract.extract(url).domain
    try:
        return domain.lower() in soup.title.text.lower()
    except:
        return False 



#--------------------------------- Deals with forms & inputs ---------------------------------
def num_of_forms(soup):
    forms = soup.find_all('form')
    return len(forms) 

def num_of_forms_with_inputs(soup):
    forms = soup.find_all('form')
    count = 0
    for form in forms:
        if form.find('input'):
            count += 1
    return count 

def get_names_of_forms_with_inputs(soup):
    forms = soup.find_all('form')
    names = []
    for form in forms:
        inputs = form.find_all('input')
        for input in inputs:
            try:
                if 'name' in input:
                    names.append(str(input['name']))
            except:
                continue
    return names

def num_of_forms_with_dropdowns(soup):
    forms = soup.find_all('form')
    count = 0
    for form in forms:
        if form.find('select'):
            count += 1
    return count 

def get_names_of_forms_with_dropdowns(soup):
    forms = soup.find_all('form')
    names = []
    for form in forms:
        dropdowns = form.find_all('select')
        for dropdown in dropdowns:
            try:
                if 'name' in dropdown:
                    names.append(str(dropdown['name']))
            except:
                continue
    return names

def num_of_forms_with_textareas(soup):
    forms = soup.find_all('form')
    count = 0
    for form in forms:
        if form.find('textareas'):
            count += 1
    return count 

def get_names_of_forms_with_textareas(soup):
    forms = soup.find_all('form')
    names = []
    for form in forms:
        textareas = form.find_all('textareas')
        for textarea in textareas:
            try:
                if 'name' in textarea:
                    names.append(str(textarea['name']))
            except:
                continue
    return names


def get_list_of_buttons(soup):
    # Find all <button> elements
    button_tags = soup.find_all('button')  

    # Find <input> elements with type="button", "submit", or "reset"
    input_buttons = soup.find_all('input', {'type': 'button'})
    input_submits = soup.find_all('input', {'type': 'submit'})
    input_resets = soup.find_all('input', {'type': 'reset'})

    all_buttons = button_tags + input_buttons + input_submits + input_resets
    return all_buttons

def num_of_buttons(soup):
    buttons = get_list_of_buttons(soup)
    return len(buttons)


def num_of_disabled_buttons(soup):
    buttons = get_list_of_buttons(soup)
    count = 0
    for button in buttons:
        try:
            if str(button.attrs['disabled'])=='disabled':
                count += 1
        except:
            continue
    return count



#--------------------------------- Deals with links ---------------------------------
def num_of_anchor_url(soup):
    links = soup.find_all('a', href=True)
    return len(links)

def num_of_internal_external_links(soup, url):
    main_domain = tldextract.extract(url).domain
    links = soup.find_all('a', href=True)
    internal = 0
    external = 0

    for link in links:
        try:
            if "http" in link:
                domain = tldextract.extract(link).domain
                if str(domain) == main_domain:
                    internal += 1
                else:
                    external += 1
            else:
                # relative url (internal)
                internal += 1
        except:
            continue
    
    return [internal, external]

def num_of_empty_links(soup):
    links = soup.find_all('a')
    empty_count = 0

    def is_empty_link(link):
        empty_indicator = {"", "#", "#javascript::void(0)", "#content", "#skip", "javascript:;", "javascript::void(0);", "javascript::void(0)"}
        href_attr = link['href'].strip()
        return href_attr in empty_indicator

    for link in links:
        if not link.get('href') or is_empty_link(link):
            empty_count += 1
    
    return empty_count
    
def num_of_link_tags(soup):
    return len(soup.find_all("link"))


def get_source_link(soup):
    src = []
    links = soup.find_all('link')
    for link in links:
        try:
            src.append(link.attrs['href'])
        except:
            continue
    
    tag_list = ['img', 'script', 'noscript']
    for tag in tag_list:
        tags = soup.find_all(tag)
        for t in tags:
            try:
                src.append(t.attrs['src'])
            except:
                continue
    return src

def num_of_icon_rs(soup):
    return len(soup.find_all("link", rel='icon'))



#--------------------------------- Deals with iframes ---------------------------------
def num_of_iframes(soup):
    return len(soup.find_all("iframe"))

# width, height and frameborder attribute are all 0
# Or styles that make an iframe invisible
def num_of_invisible_iframes(soup):
    iframes = soup.find_all('iframe')
    count = 0
    for iframe in iframes:
        style = iframe.get('style', '').lower()
        hasNoWidth = iframe.get('width') == '0'
        hasNoHeight = iframe.get('height') == '0'
        hasNoFrameBorder = iframe.get('frameborder') == '0'
        if (hasNoWidth and hasNoHeight and hasNoFrameBorder):
            count += 1
        elif ('display: none' in style or 'visibility: hidden' in style):
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


# Get an external re-direction link that is present in the iframe if any
def iframe_src_analysis(soup):
    iframes = soup.find_all('iframe')
    src_attributes = []
    for iframe in iframes:
        src = iframe.get('src')
        if src:
            src_attributes.append(src)
    
    return src_attributes
    


#--------------------------------- Deals with auto redirects/refreshes ---------------------------------
def num_of_auto_redirect(soup):
    meta_refresh = soup.find_all('meta', {'http-equiv': 'refresh'})
    return len(meta_refresh)

# Content is typically = "time;url=target_url".
def auto_redirect_url(soup):
    meta_refresh = soup.find_all('meta', {'http-equiv': 'refresh'})
    urls = []

    for meta in meta_refresh:
        content = meta.get('content')
        if content:
            parts = content.split(';')
            for part in parts:
                if part.strip().lower().startswith('url='):
                    # Extract the URL part
                    url = part.strip()[4:]
                    urls.append(url)

    return urls
    


#--------------------------------- Deals with pop-up window ---------------------------------
def num_of_pop_up(soup):
    scripts = soup.find_all('script')
    pop_up = 0
    for script in scripts:
        try:
            if('alert' in str(script.contents)) or ('window.open' in str(script.contents)):
                pop_up += 1
        except:
            continue
    
    return pop_up
    


#--------------------------------- Deals with styles ---------------------------------
# Searches for <link> tags with the rel attribute set to "stylesheet"
def num_of_stylesheets_total(soup):
    link_tags = soup.find_all('link', rel='stylesheet')
    return len(link_tags) 

# Returns the number of css  present in the HTML Script
# Searches for <link> tags with the rel attribute set to "stylesheet", type attribute set to "text/css" 
def num_of_css_stylesheets(soup):
    link_tags = soup.find_all('link', rel='stylesheet', type='text/css')
    return len(link_tags) 

# Searches <style> tags
def num_of_internal_css(soup):
    style_tags = soup.find_all('style')
    return len(style_tags)
 


#--------------------------------- Deals with scripts ---------------------------------
def num_of_noscripts(soup):
    num = len(soup.find_all("noscript"))
    return num

def num_of_scripts(soup):
    num = len(soup.find_all("script"))
    return num

def num_of_inline_scripts(soup):
    script_elements = soup.find_all('script')
    count = 0

    for script in script_elements:
        if not script.has_attr('src'):
            count += 1

    return count

def num_of_inline_js_scripts(soup):
    def is_js(script):
        return not script.has_attr('type') or script['type'] in ["text/javascript", "application/javascript"]
    
    script_elements = soup.find_all('script')
    count = 0

    for script in script_elements:
        if not script.has_attr('src') and is_js(script):
            count += 1

    return count

def num_of_external_scripts(soup):
    script_elements = soup.find_all('script')
    count = 0

    for script in script_elements:
        if script.has_attr('src'):
            count += 1

    return count



#--------------------------------- Deals with other external contents ---------------------------------
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



#--------------------------------- Deals with media and graphics ---------------------------------
def num_of_imgs(soup):
    num = len(soup.find_all("img"))
    return num

def num_of_pictures(soup):
    num = len(soup.find_all("picture"))
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

def num_of_clickable_image_maps(soup):
    num = len(soup.find_all("map"))
    return num

def num_of_canvas(soup):
    num = len(soup.find_all("canvas"))
    return num