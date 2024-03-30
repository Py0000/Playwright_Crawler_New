import io
from PIL import Image
from bs4 import BeautifulSoup

class HtmlExtractor:
    def __init__(self):
        pass
    
    def extract_title(self, soup):
        title_tag = soup.title
        return title_tag.string.strip() if title_tag else 'Not Found'

    def extract_meta_description(self, soup):
        meta_description = soup.find('meta', attrs={'name': 'description'})
        return meta_description['content'] if meta_description and meta_description.has_attr('content') else 'Not Found'
    
    def extract_favicon(self, soup):
        favicon = soup.find('link', rel='icon')
        return favicon['href'] if favicon and favicon.has_attr('href') else 'Not Found'
    
    def extract_logo_alt_text(self, soup):
        logo_image = soup.find('img', attrs={'class': 'logo', 'alt': True})
        return logo_image['alt'] if logo_image and logo_image.has_attr('alt') else 'Not Found'
    
    def extract_footer_text(self, soup):
        footer = soup.find('footer') or soup.find('div', class_='footer')
        return footer.text.strip() if footer else 'Not Found'
    
    def extract_header_text(self, soup):
        headers_text = [header.text.strip() for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header'])]
        return ' | '.join(headers_text) if headers_text else 'Not Found'

    def extract_nav_bar_content(self, soup):
        nav_content = soup.find('nav')
        return nav_content.text.strip() if nav_content else 'Not Found'
    
    def extract_textual_info(self, soup, tag_name):
        texts = [tag.text.strip() for tag in soup.find_all(tag_name)]
        return ' | '.join(texts) if texts else 'Not Found'
    
    def extract_relevant_info_from_html(self, html_content):
        soup = BeautifulSoup(html_content, 'lxml')
        brand_info = {
            'title': self.extract_title(soup),
            'meta_description': self.extract_meta_description(soup),
            'favicon': self.extract_favicon(soup),
            'logo_alt_text': self.extract_logo_alt_text(soup),
            'footer_text': self.extract_footer_text(soup),
            'headers_text': self.extract_headers_text(soup),
            'nav_bar_content': self.extract_nav_bar_content(soup),
            'paragraphs_text': self._extract_tag_text(soup, 'p'),
            'span_text': self._extract_tag_text(soup, 'span')
        }
        
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