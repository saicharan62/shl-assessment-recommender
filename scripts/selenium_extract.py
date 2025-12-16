"""
selenium_extract.py

Extract SHL Individual Test Solutions (type=1)
with pagination, throttling tolerance, and checkpoint saving.
"""

import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

BASE_URL = "https://www.shl.com/products/product-catalog/"
OUTPUT_PATH = "data/shl_catalog.csv"

PAGE_SIZE = 12
MAX_EMPTY_PAGES = 3
CHECKPOINT_EVERY = 1        # save after every page
MIN_ACCEPTABLE_ROWS = 300  # safe lower bound


def save_checkpoint(products: dict):
    """Save current progress to CSV (idempotent)."""
    if not products:
        return
    df = pd.DataFrame(
        [{"name": name, "url": url} for url, name in products.items()]
    )
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"[checkpoint] saved {len(df)} rows to {OUTPUT_PATH}")


def main():
    driver = webdriver.Chrome()
    print("Chrome launched")

    products = {}
    start = 0
    page = 1
    empty_pages = 0

    try:
        while True:
            url = f"{BASE_URL}?start={start}&type=1"
            print(f"\nOpening page {page}: {url}")

            try:
                driver.get(url)
                time.sleep(8)
                links = driver.find_elements(By.TAG_NAME, "a")
            except Exception as e:
                print(f"Browser/session error on page {page}: {e}")
                print("Stopping pagination safely.")
                break

            page_products = {}

            for link in links:
                name = link.text.strip()
                href = link.get_attribute("href")

                if not name or not href:
                    continue

                if "/products/product-catalog/view/" not in href:
                    continue

                page_products[href] = name

            page_count = len(page_products)
            print(f"Products found on page {page}: {page_count}")

            if page_count == 0:
                empty_pages += 1
                print(f"Empty pages in a row: {empty_pages}")
            else:
                empty_pages = 0
                products.update(page_products)

            print(f"Total collected so far: {len(products)}")

            # 🔒 CHECKPOINT SAVE (key fix)
            save_checkpoint(products)

            if empty_pages >= MAX_EMPTY_PAGES:
                print("Multiple empty pages detected. Stopping pagination.")
                break

            start += PAGE_SIZE
            page += 1

    finally:
        # 🔒 FINAL SAVE (even if browser crashes)
        save_checkpoint(products)
        driver.quit()
        print("Chrome closed")

    # ---- Post-run validation ----
    final_count = len(products)
    print(f"\nFinal product count in memory: {final_count}")

    if final_count < MIN_ACCEPTABLE_ROWS:
        raise ValueError(
            f"Too few assessments extracted ({final_count}). "
            "Try rerunning after cooldown."
        )

    print("Extraction completed successfully.")


if __name__ == "__main__":
    main()
