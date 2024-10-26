import unittest
import json
import httpx
from fake_useragent import UserAgent
import time
from login_harvest import LoginHarvest

# Load login URLs from JSON file
with open("login_urls.json") as f:
    LOGIN_URLS = json.load(f)

# Dynamically get a User-Agent for every request to make it more like a real browser.
user_agent = UserAgent()

def create_header(website_url):
    return {
        'User-Agent': user_agent.random,  # Dynamically generated User-Agent
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        "Referer": website_url,
        "Origin": website_url,
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
    }

class TestLoginHarvestWithUrls(unittest.TestCase):

    def test_extract_from_login_pages(self):
        """Test extracting login elements from the given list of URLs."""
        for url in LOGIN_URLS:
            with self.subTest(url=url):
                try:
                    with httpx.Client(verify=False, follow_redirects=True) as client:
                        # Add dynamic headers with a new user agent for every request
                        headers = create_header(url)
                        response = client.get(url, headers=headers, timeout=30)
                        response.raise_for_status()  # Ensure we got a valid response

                        html_content = response.text

                        # Instantiate LoginHarvest with HTML content and analyze it
                        harvest = LoginHarvest(html_content)
                        extracted_data = harvest.analyze_login_form()

                        # Check if extraction provides some relevant output (not empty)
                        self.assertTrue(len(extracted_data['form_elements']['inputs']) > 0, f"No input fields extracted from {url}")
                        self.assertTrue(len(extracted_data['form_elements']['buttons']) > 0, f"No buttons extracted from {url}")
                        self.assertTrue(len(extracted_data['relevant_elements']) > 0, f"No relevant elements extracted from {url}")
                        self.assertTrue(len(extracted_data['form_elements']['forms']) < 100, f"Form extraction from {url} exceeds limit")

                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 503:
                        self.skipTest(f"Skipping test for {url} due to server unavailability (503).")
                    elif e.response.status_code in [301, 302, 403, 400]:
                        # Handle common errors like redirections or forbidden requests
                        self.skipTest(f"Skipping test for {url} due to redirection or forbidden status.")
                    else:
                        self.fail(f"Request to {url} failed: {e}")

                except httpx.RequestError as e:
                    self.fail(f"Request to {url} failed: {e}")

                # Throttle requests to prevent being blocked
                time.sleep(3)

if __name__ == "__main__":
    unittest.main()
