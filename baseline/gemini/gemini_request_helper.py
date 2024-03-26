import io
from PIL import Image

import os
import zipfile
from bs4 import BeautifulSoup

class HtmlExtractor:
    def __init__(self):
        pass

    def open_html_file(self, html_file_path):
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        return html_content


    def extract_relevant_info_from_html(self, html_content):
        brand_info = {}
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Extract title
        title_tag = soup.title
        brand_info['title'] = title_tag.string if title_tag else 'Not Found'
        
        # Extract meta description
        # This attribute defines a description of your web page
        meta_description = soup.find('meta', attrs={'name': 'description'})
        if meta_description and meta_description.has_attr('content'):
            brand_info['meta_description'] = meta_description['content'] 
        else:
            brand_info['meta_description'] = 'Not Found'

        # Extract favicon
        favicon = soup.find('link', rel='icon')
        if favicon and favicon.has_attr('href'):
            brand_info['favicon'] = favicon['href'] 
        else:
            brand_info['favicon'] = 'Not Found'

        # Extract logo alt text
        logo_image = soup.find('img', attrs={'class': 'logo', 'alt': True})
        if logo_image and logo_image.has_attr('alt'):
            brand_info['logo_alt_text'] = logo_image['alt'] 
        else:
            brand_info['logo_alt_text'] = 'Not Found'
        
        # Footer copyright
        footer = soup.find('footer') or soup.find('div', class_='footer')
        if footer:
            brand_info['footer_text'] = footer.text.strip()
        else:
            brand_info['footer_text'] = 'Not Found'
        
        # Extracting header elements (h1, h2, header)
        headers_text = []
        for header in soup.find_all(['h1', 'h2', 'header']):
            headers_text.append(header.text.strip())
        if headers_text:
            brand_info['headers_text'] = ' | '.join(headers_text) 
        else: 
            brand_info['headers_text'] = 'Not Found'
        
        # Extracting navigation bar content
        nav_content = soup.find('nav')
        if nav_content:
            brand_info['nav_bar_content'] = nav_content.text.strip()
        else:
            brand_info['nav_bar_content'] = 'Not Found'

        brand_info_str = "\n".join(f"{key}: {value}" for key, value in brand_info.items())
        
        return brand_info_str


class ImageCompressor:
    def __init__(self):
        pass

    def compress_image(self, image, quality):
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG', quality=quality)
        img_bytes.seek(0)

        new_image = Image.open(img_bytes)
        return new_image
