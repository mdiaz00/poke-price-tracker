# scraper/fetch_tcgplayer.py

import requests
from bs4 import BeautifulSoup
import datetime
from database.save_to_db import get_or_create_card, save_sales
from database.db_init import SessionLocal

# Define condition tags
CONDITION_TAGS = {
    "mint": ["Mint"],
    "near_mint": ["Near Mint"],
    "light_play": ["Lightly Played"],
    "moderate_play": ["Moderately Played"],
    "damaged": ["Damaged", "Heavily Played"],
}


def get_condition(title):
    """Determine the condition based on title."""
    title = title.lower()
    for condition, keywords in CONDITION_TAGS.items():
        if any(keyword.lower() in title for keyword in keywords):
            return condition
    return "unknown"


def fetch_tcgplayer_prices(card_name):
    """Fetch market listings from TCGPlayer."""
    search_query = card_name.replace(" ", "%20")
    url = f"https://www.tcgplayer.com/search/pokemon/product?productLineName=pokemon&ListingType=Listings&searchTerm={search_query}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    listed_items = []
    today = datetime.datetime.now()

    listings = soup.select('.search-result__market-price')  # Scraping Market Prices

    for listing in listings:
        try:
            price_text = listing.get_text().strip().replace("$", "").replace(",", "")
            price = float(price_text)
        except (ValueError, AttributeError):
            continue

        # Assume most TCGPlayer market prices are Near Mint unless otherwise specified
        condition = "near_mint"

        listed_items.append({
            "price": price,
            "condition": condition,
            "source": "tcgplayer",
            "sold_date": today,  # For consistency, we can use "today" for now
        })

    return listed_items


if __name__ == "__main__":
    card = input("Enter card name and number (e.g. Rosa 236/236): ")

    # Fetch
    tcg_items = fetch_tcgplayer_prices(card)

    print(f"\nRecent TCGPlayer market prices for {card}:\n")
    for item in tcg_items:
        print(f"Price: ${item['price']} - Condition: {item['condition']}")

    # Save to database
    db = SessionLocal()
    card_obj = get_or_create_card(db, card)
    save_sales(db, card_obj, tcg_items)
    db.close()

    print("\n✅ TCGPlayer listings saved to database successfully!")
