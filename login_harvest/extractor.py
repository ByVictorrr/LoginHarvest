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
        self.element_analyzer = ElementAnalyzer(
            keywords=['login', 'sign in', 'signin', 'username', 'password', 'continue', 'next'],
            oauth_providers=self.oauth_providers
        )
        self.form_analyzer = FormAnalyzer()

    def extract_relevant_html(self, html_content):
        """Extract the most relevant parts of the HTML content to find login fields, in a generalized way."""
        soup = BeautifulSoup(html_content, 'html.parser')
        extracted_elements = []

        # Extract and analyze forms
        form_data = self.form_analyzer.extract_forms(soup)
        login_form = self.form_analyzer.extract_login_form(form_data)
        if login_form:
            xpath = self.generate_xpath(BeautifulSoup(login_form['form_html'], 'html.parser').form)
            extracted_elements.append(f"<!-- LOGIN FORM --> {login_form} | XPath: {xpath}")

        # Extract and analyze individual elements using ElementAnalyzer
        for tag in self.element_analyzer.relevant_tags:
            elements = soup.find_all(tag)
            for element in elements:
                analyzed_element = self.element_analyzer.analyze_element(element)
                if analyzed_element['score'] > 0:  # Only include relevant elements with a positive score
                    xpath = self.generate_xpath(element)
                    extracted_elements.append(
                        f"<!-- RELEVANT ELEMENT --> {str(analyzed_element['element'])} | XPath: {xpath}")

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
            idx = 1  # XPath indices are 1-based

            # Iterate through siblings and find the index of the current element
            for sibling in siblings:
                if sibling == element:
                    components.append(f"{element.name}[{idx}]")
                    break
                idx += 1
            else:
                # If there is only one element of that type, no index is needed
                components.append(element.name)

        components.reverse()
        return "/" + "/".join(components)


if __name__ == "__main__":
    pass
