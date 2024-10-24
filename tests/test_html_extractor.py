import unittest
import json
import requests
from login_harvest import HtmlExtractor, OAUTH_PROVIDERS

# Load login URLs from JSON file
with open("login_urls.json") as f:
    LOGIN_URLS = json.load(f)


class TestHtmlExtractorWithUrls(unittest.TestCase):

    def setUp(self):
        """Set up the HtmlExtractor instance for testing."""
        self.extractor = HtmlExtractor(oauth_providers=OAUTH_PROVIDERS)

    def test_extract_from_login_pages(self):
        """Test extracting login elements from the given list of URLs."""
        for url in LOGIN_URLS:
            with self.subTest(url=url):
                try:
                    response = requests.get(url, timeout=10, verify=False)
                    response.raise_for_status()  # Ensure we got a valid response

                    html_content = response.text
                    extracted_content = self.extractor.extract_relevant_html(html_content)

                    # Check if extraction provides some relevant output (not empty)
                    self.assertTrue(len(extracted_content) > 0, f"No relevant content extracted from {url}")

                except requests.exceptions.HTTPError as e:
                    if response.status_code == 503:
                        self.skipTest(f"Skipping test for {url} due to server unavailability (503).")
                    else:
                        self.fail(f"Request to {url} failed: {e}")

                except requests.exceptions.RequestException as e:
                    self.fail(f"Request to {url} failed: {e}")


if __name__ == "__main__":
    unittest.main()
