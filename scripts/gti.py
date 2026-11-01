import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import bs4
import requests

ARCHIVE_URL = "https://cloud.google.com/blog/topics/threat-intelligence/"
API_URL = "https://cloud.google.com/blog/_/TransformBlogUi/data/batchexecute"
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "gti_reports.json"
RPC_ID = "SQC9mf"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def fetch_archive_page(
    session: requests.Session, page_token: str, curated_articles: str
) -> tuple[list[list[Any]], str]:
    request_data = json.dumps(
        [
            "cloudblog",
            "en",
            None,
            None,
            10,
            page_token,
            "article",
            ["threat-intelligence"],
            [curated_articles],
        ],
        separators=(",", ":"),
    )
    response = session.post(
        API_URL,
        params={
            "rpcids": RPC_ID,
            "source-path": "/blog/topics/threat-intelligence/",
            "hl": "en-US",
            "soc-app": "1",
            "soc-platform": "1",
            "soc-device": "1",
            "rt": "c",
        },
        data={
            "f.req": json.dumps(
                [[[RPC_ID, request_data, None, "generic"]]],
                separators=(",", ":"),
            )
        },
        headers={"X-Same-Domain": "1", "Referer": "https://cloud.google.com/"},
        timeout=(5, 20),
    )
    response.raise_for_status()

    lines = response.text.splitlines()
    payload_index = next(
        (index + 1 for index, line in enumerate(lines[:-1]) if line.isdecimal()),
        None,
    )
    if payload_index is None:
        raise ValueError("Google archive response did not contain a data payload")

    rpc_response = json.loads(lines[payload_index])[0]
    if rpc_response[0] != "wrb.fr" or rpc_response[1] != RPC_ID:
        raise ValueError("Google archive response contained an unexpected RPC result")

    payload = json.loads(rpc_response[2])
    if not isinstance(payload, list) or len(payload) < 2:
        raise ValueError("Google archive response had an unexpected payload format")
    posts, next_page_token = payload[0], payload[1]
    if not isinstance(posts, list) or not isinstance(next_page_token, str):
        raise ValueError("Google archive response had invalid pagination data")
    return posts, next_page_token


def extract_article_text(session: requests.Session, url: str) -> str:
    response = session.get(url, timeout=(5, 20))
    response.raise_for_status()
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    article = soup.select_one("article .OYL9D") or soup.find("article")
    if article is None:
        raise ValueError(f"Could not find article body at {url}")
    return article.get_text(" ", strip=True)


def main() -> None:
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=365)
    reports = {}

    with requests.Session() as session:
        session.headers.update(HEADERS)
        archive_response = session.get(ARCHIVE_URL, timeout=(5, 20))
        archive_response.raise_for_status()
        archive_soup = bs4.BeautifulSoup(archive_response.text, "html.parser")
        listing = archive_soup.select_one(
            "[data-next-page-token][data-curated-articles]"
        )
        if listing is None:
            raise ValueError("Could not find Google Threat Intelligence archive data")
        curated_articles = listing["data-curated-articles"]
        if not isinstance(curated_articles, str):
            raise ValueError("Google archive did not provide a valid article cursor")

        page_token = "1"
        while True:
            posts, next_page_token = fetch_archive_page(
                session, page_token, curated_articles
            )
            if not posts:
                break

            oldest_published = None
            for post in posts:
                title = post[1]
                url = post[7]
                timestamp = post[8][0]
                published = datetime.fromtimestamp(timestamp, timezone.utc)
                oldest_published = published
                if cutoff <= published <= now:
                    reports[title] = extract_article_text(session, url)
                    time.sleep(0.2)

            print(f"Processed archive page {page_token}: {len(posts)} posts")
            if oldest_published is not None and oldest_published < cutoff:
                break
            if next_page_token == page_token:
                raise ValueError("Google archive pagination did not advance")
            page_token = next_page_token

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(reports, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Saved {len(reports)} reports to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
