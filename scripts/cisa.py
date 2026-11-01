import requests

FEED = "https://www.cisa.gov/cybersecurity-advisories/all.xml"

headers = {
    "User-Agent": "Mozilla/5.0"
}

if __name__ == "__main__":
    response = requests.get(FEED, headers=headers)

    print(response.status_code)
    print(response.text[:2000])