import json
from pathlib import Path

import requests
import bs4

API_URL = "https://www.microsoft.com/en-us/security/blog/wp-json/wp/v2/posts"
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "mti_reports.json"
params = {
    "after": "2025-10-28T00:00:00",
    "before": "2026-10-29T00:00:00",
    "per_page": 100,
    "page": 1,
    "topic": 3687,
    "_fields": "date,link,title,content",
}

reports = {}
page = 1

while True:
    params["page"] = page
    response = requests.get(API_URL, params=params, timeout=(5, 20))
    response.raise_for_status()
    posts = response.json()

    for post in posts:
        title = post["title"]["rendered"]
        html_body = post["content"]["rendered"]
        body = bs4.BeautifulSoup(html_body, "html.parser").get_text(" ", strip=True)
        reports[title] = body

    total_pages = int(response.headers.get("X-WP-TotalPages", "1"))
    print(f"Fetched page {page}/{total_pages}: {len(posts)} posts")
    if page >= total_pages:
        break
    page += 1

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH.write_text(
    json.dumps(reports, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print(f"Saved {len(reports)} reports to {OUTPUT_PATH}")
