from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database.db_init import SessionLocal, init_db
from database.models import Card, Sale
from data.calculate_median import calculate_medians
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/card/{card_name}")
def get_card_info(
    card_name: str,
    condition: Optional[str] = None,
    sort_by: Optional[str] = "sold_date",
    sort_order: Optional[str] = "desc",
    db: Session = Depends(get_db)
):
    card = db.query(Card).filter(Card.name == card_name).first()

    # Fallback to first partial match if exact not found
    if not card:
        card = db.query(Card).filter(Card.name.ilike(f"%{card_name}%")).first()

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    sales_query = db.query(Sale).filter(Sale.card_id == card.id)

    if condition:
        sales_query = sales_query.filter(Sale.condition == condition)

    if sort_by == "price":
        if sort_order == "asc":
            sales_query = sales_query.order_by(Sale.price.asc())
        else:
            sales_query = sales_query.order_by(Sale.price.desc())
    else:
        if sort_order == "asc":
            sales_query = sales_query.order_by(Sale.sold_date.asc())
        else:
            sales_query = sales_query.order_by(Sale.sold_date.desc())

    sales = sales_query.all()
    medians = calculate_medians(sales)

    return {
        "card_name": card.name,
        "set_number": card.set_number,
        "medians": medians,
        "sales": [
            {
                "price": s.price,
                "condition": s.condition,
                "sold_date": s.sold_date.strftime("%Y-%m-%d")
            } for s in sales
        ]
    }

@app.get("/trending")
def get_trending_cards(db: Session = Depends(get_db)):
    recent_sales = db.query(Sale).order_by(Sale.sold_date.desc()).limit(100).all()
    card_ids = list(set([s.card_id for s in recent_sales]))
    trending_cards = db.query(Card).filter(Card.id.in_(card_ids)).all()
    return [
        {
            "name": card.name,
            "set_number": card.set_number
        } for card in trending_cards
    ]

@app.get("/search")
def search_cards(q: str = Query(..., min_length=2), db: Session = Depends(get_db)):
    results = db.query(Card).filter(Card.name.ilike(f"%{q}%")).all()
    return [{"id": c.id, "name": c.name, "set_number": c.set_number} for c in results]
