import os
import json
from bs4 import BeautifulSoup

# Load OAuth providers from JSON file
oauth_providers_path = os.path.join(os.path.dirname(__file__), "oauth_providers.json")
with open(oauth_providers_path) as oauth_fp:
    OAUTH_PROVIDERS = json.load(oauth_fp)


class HtmlExtractor:
    def __init__(self, oauth_providers=OAUTH_PROVIDERS):
        self.oauth_providers = oauth_providers
        self.relevant_tags = ['input', 'button', 'form', 'iframe', 'a']
        self.relevant_attributes = {
            'input': ['type', 'name', 'placeholder'],
            'button': ['type', 'name', 'value', 'class', 'text'],
            'a': ['href', 'class', 'text'],
            'iframe': ['src']
        }
        self.keywords = ['login', 'sign in', 'signin', 'username', 'password', 'continue', 'next',
                         'oauth'] + self.oauth_providers
        self.generalized_xpaths = [
            "//*[contains(text(),'Next')]",
            "//*[contains(text(),'Sign in')]",
            "//*[contains(text(),'Login')]",
            "//*[contains(text(),'Continue')]"
        ]

    def extract_relevant_html(self, html_content):
        """Extract the most relevant parts of the HTML content to find login fields, in a generalized way."""
        soup = BeautifulSoup(html_content, 'html.parser')
        extracted_elements = []

        # Iterate through each relevant tag to find matching elements
        for tag in self.relevant_tags:
            elements = soup.find_all(tag)
            for element in elements:
                element_str = str(element).lower()

                # Check if the element contains any of the keywords
                if any(keyword in element_str for keyword in self.keywords):
                    xpath = self.generate_xpath(soup, element)
                    extracted_elements.append({'html': str(element), 'xpath': xpath})
                    continue

                # For more specific filtering, check the attributes of each element
                for attr in self.relevant_attributes.get(tag, []):
                    attr_value = element.attrs.get(attr, '')

                    if isinstance(attr_value, str):
                        attr_value_lower = attr_value.lower()
                        if any(keyword in attr_value_lower for keyword in self.keywords):
                            xpath = self.generate_xpath(soup, element)
                            extracted_elements.append({
                                'html': f"<!-- {tag.upper()} FIELD WITH {attr.upper()} CONTAINING LOGIN KEYWORDS --> {str(element)}",
                                'xpath': xpath
                            })
                            break
                    elif isinstance(attr_value, list):
                        # If the attribute value is a list, iterate over it and check if any item contains a keyword
                        for value in attr_value:
                            if any(keyword in value.lower() for keyword in self.keywords):
                                xpath = self.generate_xpath(soup, element)
                                extracted_elements.append({
                                    'html': f"<!-- {tag.upper()} FIELD WITH {attr.upper()} CONTAINING LOGIN KEYWORDS --> {str(element)}",
                                    'xpath': xpath
                                })
                                break

                # For input fields, try to identify potential username or password attributes
                if tag == 'input':
                    input_type = element.attrs.get('type', '').lower()
                    input_name = element.attrs.get('name', '').lower()
                    input_placeholder = element.attrs.get('placeholder', '').lower()

                    if 'password' in input_type:
                        xpath = self.generate_xpath(soup, element)
                        extracted_elements.append({'html': f"<!-- PASSWORD FIELD --> {str(element)}", 'xpath': xpath})
                    elif any(keyword in input_name for keyword in ['user', 'email', 'login']):
                        xpath = self.generate_xpath(soup, element)
                        extracted_elements.append({'html': f"<!-- USERNAME FIELD --> {str(element)}", 'xpath': xpath})
                    elif any(keyword in input_placeholder for keyword in ['user', 'email', 'login']):
                        xpath = self.generate_xpath(soup, element)
                        extracted_elements.append({'html': f"<!-- USERNAME FIELD --> {str(element)}", 'xpath': xpath})

                # Identify potential OAuth buttons or links
                if tag in ["a", "button", "div"]:
                    if any(keyword in element_str for keyword in
                           ['sign in with', 'continue with'] + self.oauth_providers):
                        xpath = self.generate_xpath(soup, element)
                        extracted_elements.append({'html': f"<!-- OAUTH BUTTON --> {str(element)}", 'xpath': xpath})

        # Add generalized xpaths to catch common buttons like "Next" or "Sign in"
        for xpath in self.generalized_xpaths:
            extracted_elements.append({'html': f"<!-- GENERALIZED XPATH --> {xpath}", 'xpath': xpath})

        # Return the extracted elements
        return extracted_elements

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
