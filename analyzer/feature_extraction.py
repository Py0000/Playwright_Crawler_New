import json
import os
import tldextract


def len_html(soup):
    return len(soup.text)

def hidden_div(soup):
    scripts = soup.find_all('div')          
    find = 0
    for script in scripts:
        try:
            if str(script.attrs['style'])=='visibility:hidden' or str(script.attrs['style'])=='display:none':
                find = 1    
                break               
        except:
            continue
    return find 

def hidden_button(soup):
        scripts = soup.find_all('button')          
        find = 0
        for script in scripts:
            try:
                if str(script.attrs['disabled'])=='disabled':
                    find = 1   
                    break
            except:
                continue
        return find 

def hidden_input(soup):
        scripts = soup.find_all('input')          
        find = 0
        for script in scripts:
            try:
                if str(script.attrs['type'])=='hidden' or str(script.attrs['disabled'])=='disabled':
                    find = 1
                    break
            except:
                continue                
        return find 

def find_all_link(soup):
        a_tags = soup.find_all('a')
        a_data = []

        for a_tag in a_tags:
            try:
                a_data.append(a_tag.attrs['href'])
            except:
                continue
        
        return a_data

def number_of_links(soup):
    link_list = find_all_link(soup)
    empty_list = empty_link(soup)

    return len(link_list) - empty_list

def empty_link(soup): ## Number of empty links
        link_list = find_all_link(soup)
        count = 0
        for j in link_list:
            if j=="" or j=="#" or j=='#javascript::void(0)' or j=='#content' or j=='#skip' or j=='javascript:;' or j=='javascript::void(0);' or j=='javascript::void(0)':
                count += 1
        if len(link_list)==0:
            return 0
        return count 

def internal_external_link(soup, url):  ## Number of internal hyperlinks and number of external hyperlinks
    link_list = find_all_link(soup)
    if len(link_list)==0:  ## in case there is no hyperlink
        return [0, 0]  
    
    count = 0
    url_domain = tldextract.extract(url).domain
    for j in link_list:
        if "http" in j:
            brand = tldextract.extract(j).domain
            if str(brand) == url_domain:
                count += 1
        else:
            count +=1                
    
    return [count, len(link_list) - count]

def find_form(soup):
        forms = soup.find_all('form')
        data = []

        for form in forms:
            input_tags = form.find_all('input')
            for input_ in input_tags:
                try:
                    if input_.has_key('name'):
                        data.append(str(input_['name']))
                except:
                    continue
        
        return data
    
def login_form(soup): ## have login-form requires password
    input_list = find_form(soup)
    result = 0
    for j in input_list:
        if j.find("password")!=-1 or j.find("pass")!=-1 or j.find("login")!=-1 or j.find("signin")!=-1:
            result = 1
            break
    return result



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


########## DEALS WITH STYLES & STYLESHEETS ##########

# Returns the number of css  present in the HTML Script
# Searches for <link> tags with the rel attribute set to "stylesheet"
def num_of_stylesheets_total(soup):
    link_tags = soup.find_all('link', rel='stylesheet')
    num = len(link_tags) 

    return num

# Returns the number of css  present in the HTML Script
# Searches for <link> tags with the rel attribute set to "stylesheet", type attribute set to "text/css" 
def num_of_css_stylesheets(soup):
    # Search for <link> tags with rel="stylesheet" and type="text/css"
    link_tags = soup.find_all('link', rel='stylesheet', type='text/css')

    num_css = len(link_tags) 

    return num_css


def find_source(soup,tag):  ## find src attribute in <img> <link> ... 
        if tag =='link':
            links = soup.find_all('link')
            link_data = []

            for link in links:
                try:
                    link_data.append(link.attrs['href'])
                except:
                    continue
            return link_data
        
        else:
            resources = soup.find_all(str(tag))
            data = []

            for resource in resources:
                try:
                    data.append(resource.attrs['src'])       
                except:
                    continue
            return data

def internal_external_resource(soup, url): ##
        tag_list = ['link','img','script','noscript']
        resource_list = []
        count = 0
        for tag in tag_list:
            resource_list.append(find_source(soup,tag))
        
        resource_list = [y for x in resource_list for y in x]
        if len(resource_list)==0: ## in case there is no resource link
            return [0, 0]

        url_domain = tldextract.extract(url).domain
        for j in resource_list:
            if "http" in j:
                if not(url_domain == tldextract.extract(j).domain):
                    count +=1   
        
        return len(resource_list) - count, count
