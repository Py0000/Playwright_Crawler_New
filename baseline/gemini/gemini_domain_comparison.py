import argparse
import tldextract
import google.generativeai as genai

from baseline.utils import utils

class DomainExtractor:
    def __init__(self):
        pass

    def extract_second_level_domain(self, url):
        extracted = tldextract.extract(url)
        return extracted.domain

class GeminiDomainComparator:
    def __init__(self) -> None:
        self.model = self.setup_model()

    def setup_model(self):
        genai.configure(api_key=utils.get_api_key("baseline/gemini/api_key_new.txt"))
        model = genai.GenerativeModel('gemini-pro')
        return model
    
    def determine_url_brand_match(self, url, brand):
        system_prompt = "You are an expert at identifying domains. I will provide you with the url of the webpage and an identified brand. Your task is to determine whether the url given belongs to the brand identified."
        response_prompt = "Return your analysis and results either as a 'Yes' if the url belongs to the brand identified (Or its parent/child organization) or 'No' if the url does not belong to the brand identified."

        prompt = f"{system_prompt}\n{response_prompt}\nHere is the url: {url} and the brand identified: {brand}"
        try:
            response = self.model.generate_content(prompt)
            response.resolve()
            result_text = response.candidates[0].content.parts[0].text
            print(result_text)
            return result_text
        except Exception as e:
            print(e)
            return "Error"
    
"""
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    parser.add_argument("url", help="url")
    parser.add_argument("brand", help="brand")
    args = parser.parse_args()

    comparator = GeminiDomainComparator()
    comparator.determine_url_brand_match(args.url, args.brand)
"""