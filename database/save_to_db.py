# database/save_to_db.py

from sqlalchemy.orm import Session
from database.models import Card, Sale
from database.db_init import SessionLocal

def get_or_create_card(db: Session, name: str, set_number: str = None):
    """Check if a card already exists, if not, create it."""
    card = db.query(Card).filter(Card.name == name).first()
    if card:
        return card

    new_card = Card(name=name, set_number=set_number)
    db.add(new_card)
    db.commit()
    db.refresh(new_card)
    return new_card

def save_sales(db: Session, card: Card, sales_data: list):
    """Save sales into the database for a specific card."""
    for sale in sales_data:
        new_sale = Sale(
            card_id=card.id,
            price=sale['price'],
            condition=sale['condition'],
            source=sale['source'],
            sold_date=sale.get('sold_date')  # sold_date is optional
        )
        db.add(new_sale)
    db.commit()

# Test function (Optional)
if __name__ == "__main__":
    db = SessionLocal()
    card_name = "Test Rosa 236/236"
    set_number = "236/236"

    # Dummy sales data for testing
    sales = [
        {"price": 279.99, "condition": "near_mint", "source": "ebay", "sold_date": None},
        {"price": 260.00, "condition": "light_play", "source": "ebay", "sold_date": None},
    ]

    card = get_or_create_card(db, card_name, set_number)
    save_sales(db, card, sales)
    db.close()
    print("Test sales saved successfully!")