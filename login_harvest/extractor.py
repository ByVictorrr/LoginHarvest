import os
import json
from bs4 import BeautifulSoup
from .analyzers import ElementAnalyzer, FormAnalyzer

# Load OAuth providers from JSON file
oauth_providers_path = os.path.join(os.path.dirname(__file__), "oauth_providers.json")
with open(oauth_providers_path) as oauth_fp:
    OAUTH_PROVIDERS = json.load(oauth_fp)


class HtmlExtractor:
    def __init__(self, oauth_providers=OAUTH_PROVIDERS):
        self.oauth_providers = oauth_providers
        # Update the instantiation of analyzers to match the revised constructors
        self.element_analyzer = ElementAnalyzer(keywords=['login', 'sign in', 'signin', 'username', 'password'], oauth_providers=self.oauth_providers)
        self.form_analyzer = FormAnalyzer()

    def extract_relevant_html(self, html_content):
        """Extract the most relevant parts of the HTML content to find login fields, in a generalized way."""
        soup = BeautifulSoup(html_content, 'html.parser')
        extracted_elements = []

        # Extract and analyze forms
        forms = soup.find_all('form')
        for form in forms:
            form_details = self.form_analyzer.extract_forms(soup)
            login_form = self.form_analyzer.extract_login_form()
            if login_form:
                xpath = self.generate_xpath(form)
                extracted_elements.append(f"<!-- LOGIN FORM --> {login_form} | XPath: {xpath}")

        # Extract and analyze individual elements using ElementAnalyzer
        for tag in self.element_analyzer.relevant_tags:
            elements = soup.find_all(tag)
            for element in elements:
                analyzed_element = self.element_analyzer.analyze_element(element)
                if analyzed_element['score'] > 0:  # Only include relevant elements with a positive score
                    xpath = self.generate_xpath(element)
                    extracted_elements.append(f"<!-- RELEVANT ELEMENT --> {str(analyzed_element['element'])} | XPath: {xpath}")

        # Add generalized xpaths to catch common buttons like "Next" or "Sign in"
        for xpath in self.element_analyzer.generalized_xpaths:
            extracted_elements.append(f"<!-- GENERALIZED XPATH --> {xpath}")

        return "\n".join(extracted_elements)

    @staticmethod
    def generate_xpath(element):
        """Generate a unique XPath for the given BeautifulSoup element."""
        components = []
        for parent in element.parents:
            siblings = parent.find_all(element.name, recursive=False)
            if len(siblings) > 1:
                idx = siblings.index(element) + 1
                components.append(f"{element.name}[{idx}]")
            else:
                components.append(element.name)
        components.reverse()
        return "/" + "/".join(components)


if __name__ == "__main__":
    pass

