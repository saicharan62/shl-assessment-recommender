"""
scrape.py

Scrapes SHL Individual Test Solutions by iterating
through paginated catalog pages and parsing HTML.

No JavaScript execution, no private APIs.
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
from time import sleep

BASE_URL = "https://www.shl.com"
CATALOG_URL = "https://www.shl.com/solutions/products/product-catalog/"
OUTPUT_PATH = "data/shl_catalog.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SHL-Scraper/1.0)"
}


def get_soup(url: str) -> BeautifulSoup:
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def extract_product_links(start: int):
    """
    Extracts product detail links from one catalog page.
    """
    url = f"{CATALOG_URL}?start={start}"
    soup = get_soup(url)

    cards = soup.select("a.product-card")
    links = []

    for card in cards:
        href = card.get("href")
        if href:
            links.append(BASE_URL + href)

    return links


def parse_product_page(url: str) -> dict:
    """
    Extracts required fields from a single product page.
    """
    soup = get_soup(url)

    def text(selector):
        el = soup.select_one(selector)
        return el.get_text(strip=True) if el else ""

    return {
        "name": text("h1"),
        "url": url,
        "description": text(".product-description"),
        "test_type": text("span.test-type"),
        "duration": text("span.duration"),
        "remote_support": text("span.remote-testing"),
        "adaptive_support": text("span.adaptive-testing"),
    }


def main():
    all_links = []
    start = 0
    page_size = 12

    print("Fetching catalog pages...")

    while True:
        links = extract_product_links(start)
        if not links:
            break

        all_links.extend(links)
        print(f"Collected {len(links)} links from page starting at {start}")

        start += page_size
        sleep(0.5)

    print(f"\nTotal product links found: {len(all_links)}")

    records = []

    for i, url in enumerate(all_links, 1):
        try:
            record = parse_product_page(url)

            # Exclude pre-packaged solutions
            if "Pre-packaged" in record["name"]:
                continue

            records.append(record)
            print(f"[{i}] Scraped: {record['name']}")
            sleep(0.5)

        except Exception as e:
            print(f"Failed to scrape {url}: {e}")

    df = pd.DataFrame(records)

    print(f"\nTotal individual assessments scraped: {len(df)}")

    if len(df) < 377:
        raise ValueError(
            "Less than 377 assessments scraped. "
            "This does not meet assignment requirements."
        )

    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved catalog to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
