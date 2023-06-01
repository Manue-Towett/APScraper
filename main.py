from concurrent.futures import ThreadPoolExecutor

import requests
import pandas as pd
from bs4 import BeautifulSoup

ACCOUNTS = []
ROOT_URL = "https://accountsplace.co.ke/categorize/all?page={}"

def extract_accounts(soup: BeautifulSoup) -> None:
    try:
        title_tag = soup.find("h3", {"class": "add-title"})
        level_tag = soup.find("div", {"class": "add-image"})

        ACCOUNTS.append({
            "name": title_tag.get_text(strip=True),
            "url": title_tag.a["href"],
            "level": level_tag.select("h4")[0].text.replace("Type: ", ""),
            "rating": level_tag.select("h4")[1].text.replace("Rating: ", ""),
            "price": soup.find("h2", {"class": "item-price"}).get_text(strip=True)
        })

        print(ACCOUNTS[-1]["name"])
    except:pass

def fetch_page(page: int) -> BeautifulSoup | None:
    while True:
        try:
            response = requests.get(ROOT_URL.format(page), timeout=2)

            print(response.status_code)

            soup = BeautifulSoup(response.text, "html.parser")

            if response.status_code == 404:
                return None

            for account in soup.select("div.item-list"):
                extract_accounts(account)

            return soup
        except:pass

def save_to_csv() -> None:
    df = pd.DataFrame(ACCOUNTS)
    df.to_csv("data.csv", index=False)

if __name__ == "__main__":
    pages = list(range(1, 311))

    with ThreadPoolExecutor(max_workers=300) as executor:
        executor.map(fetch_page, pages)

    save_to_csv()