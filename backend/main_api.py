# backend/main_api.py

from fastapi import FastAPI, HTTPException, Query
from sqlalchemy.orm import Session
from database.db_init import SessionLocal
from database.models import Card, Sale
from utils.calculate_median import calculate_median

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to PokePrice Tracker API!"}

@app.get("/card/{card_name}")
def get_card_info(
    card_name: str,
    condition: str = Query(None, description="Filter by card condition"),
    sort_by: str = Query("sold_date", description="Sort by 'price' or 'sold_date'"),
    sort_order: str = Query("desc", description="Sort 'asc' or 'desc'")
):
    db = SessionLocal()

    # Search card
    card = db.query(Card).filter(Card.name.ilike(f"%{card_name}%")).first()
    if not card:
        db.close()
        raise HTTPException(status_code=404, detail="Card not found")
    card.search_count += 1
    db.commit()
    db.refresh(card)

    # Get sales
    query = db.query(Sale).filter(Sale.card_id == card.id)

    if condition:
        query = query.filter(Sale.condition == condition)

    # Handle sorting
    if sort_by == "price":
        if sort_order == "asc":
            query = query.order_by(Sale.price.asc())
        else:
            query = query.order_by(Sale.price.desc())
    else:  # default to sorting by sold_date
        if sort_order == "asc":
            query = query.order_by(Sale.sold_date.asc())
        else:
            query = query.order_by(Sale.sold_date.desc())

    sales = query.all()

    if not sales:
        db.close()
        raise HTTPException(status_code=404, detail="No sales found for this card")

    # Group prices by condition
    conditions = {}
    for sale in sales:
        cond = sale.condition
        if cond not in conditions:
            conditions[cond] = []
        conditions[cond].append(sale.price)

    # Calculate medians
    medians = {}
    for cond, prices in conditions.items():
        medians[cond] = calculate_median(prices)

    # Create result
    result = {
        "card_name": card.name,
        "set_number": card.set_number,
        "medians": medians,
        "sales": [
            {
                "price": sale.price,
                "condition": sale.condition,
                "source": sale.source,
                "sold_date": sale.sold_date,
            } for sale in sales
        ]
    }

    db.close()
    return result

@app.get("/trending")
def get_trending_cards(limit: int = 5):
    db = SessionLocal()

    trending = db.query(Card).order_by(Card.search_count.desc()).limit(limit).all()

    result = [
        {
            "card_name": card.name,
            "set_number": card.set_number,
            "search_count": card.search_count
        }
        for card in trending
    ]

    db.close()
    return result
