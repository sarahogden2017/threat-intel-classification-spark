"""
web_scraper.py

Scrapes historical web content from threat intel sources and outputs data into JSON format.

Author: Sarah Ogden
Course: DSC499
Date: 2026-10-28

Workflow:
1. Fetch historical web content from threat intel sources.
2. Parse and extract relevant data.
3. Output the data into JSON format.
"""
import json
import bs4
import requests

SOURCES = [
    # "https://cloud.google.com/blog/topics/threat-intelligence" not scrapable due to dynamic content
    "https://www.microsoft.com/en-us/security/blog/topic/threat-intelligence/"
]

HEADERS = {'User-Agent': 'Mozilla/5.0'}

if __name__ == "__main__":
    for url in SOURCES:
        print(f"Fetching content from {url}")

        resp = requests.get(url, headers=HEADERS)
        html_content = resp.text
        soup = bs4.BeautifulSoup(html_content, "html.parser")
        print(soup.prettify())

        