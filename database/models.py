# database/models.py

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Card(Base):
    __tablename__ = 'cards'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    set_number = Column(String, nullable=True)
    search_count = Column(Integer, default=0)   # 🔥 New: How many times it was searched
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Sale(Base):
    __tablename__ = 'sales'

    id = Column(Integer, primary_key=True)
    card_id = Column(Integer, ForeignKey('cards.id'), nullable=False)   # Links to the Card
    price = Column(Float, nullable=False)       # Price in dollars
    condition = Column(String, nullable=False)  # mint, near_mint, light_play, moderate_play, damaged
    source = Column(String, nullable=False)     # ebay or tcgplayer
    sold_date = Column(DateTime(timezone=True), nullable=True) # Date when it was sold or listed
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # When we scraped it
