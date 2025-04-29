# scraper/fetch_ebay.py

import requests
from bs4 import BeautifulSoup
from database.save_to_db import get_or_create_card, save_sales
from database.db_init import SessionLocal
import datetime

# Define condition tags
CONDITION_TAGS = {
    "mint": ["mint"],
    "near_mint": ["near mint", "nm"],
    "light_play": ["light play", "lp"],
    "moderate_play": ["moderate play", "mp", "moderate"],
    "damaged": ["damaged", "heavy play", "hp", "crease", "bend", "crack"],
}

def get_condition(title):
    title = title.lower().replace("/", " ").replace("-", " ")

    if "mint" in title and "near mint" not in title and "light" not in title:
        return "mint"
    if "near mint" in title or "nm" in title:
        return "near_mint"
    if "light play" in title or "lp" in title:
        return "light_play"
    if "moderate play" in title or "mp" in title:
        return "moderate_play"
    if "damaged" in title or "heavy play" in title or "hp" in title or "crease" in title or "bend" in title:
        return "damaged"
    return "unknown"


import datetime  # ADD THIS AT THE TOP

def fetch_sold_prices(card_name):
    """Fetch sold prices from eBay and assign today's date."""
    search_query = card_name.replace(" ", "+")
    url = f"https://www.ebay.com/sch/i.html?_nkw={search_query}&LH_Sold=1&LH_Complete=1"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    sold_items = []
    items = soup.select('.s-item')

    today = datetime.datetime.now()   # 🎯 Grab today's date once

    for item in items:
        title_elem = item.select_one('.s-item__title')
        price_elem = item.select_one('.s-item__price')

        if not title_elem or not price_elem:
            continue

        title = title_elem.get_text().lower()
        price_text = price_elem.get_text().replace("$", "").replace(",", "").strip()

        try:
            price = float(price_text)
        except ValueError:
            continue

        condition = get_condition(title)

        sold_items.append({
            "price": price,
            "condition": condition,
            "source": "ebay",
            "sold_date": today,  # 🎯 Set sold date = today
        })

    return sold_items




if __name__ == "__main__":
    # Ask user for card
    card = input("Enter card name and number (e.g. Rosa 236/236): ")

    # Fetch prices
    sold_items = fetch_sold_prices(card)

    # Print to screen
    print(f"\nRecent verified sold items for {card}:\n")
    for item in sold_items:
        print(f"Price: ${item['price']} - Condition: {item['condition']}")

    # Save to database
    db = SessionLocal()
    card_obj = get_or_create_card(db, card)
    save_sales(db, card_obj, sold_items)
    db.close()

    print("\n✅ Sales saved to database successfully!")
