"""
SQLAlchemy Models for CartIQ Database Schema (Supabase PostgreSQL / SQLite).
"""

from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class ProductModel(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)
    canonical_name = Column(String, nullable=False, index=True)
    brand = Column(String, index=True)
    model = Column(String, index=True)
    category = Column(String, index=True)
    features = Column(Text, nullable=True)  # JSON or comma-separated
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to marketplace offers (1-to-many)
    offers = relationship("ProductOfferModel", back_populates="product", cascade="all, delete-orphan")

class ProductOfferModel(Base):
    __tablename__ = "product_offers"

    id = Column(String, primary_key=True, index=True)
    product_id = Column(String, ForeignKey("products.id"), nullable=False, index=True)
    marketplace = Column(String, nullable=False, index=True)
    source_product_id = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=True)
    currency = Column(String, default="INR")
    discount = Column(Float, default=0.0)
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    availability = Column(Boolean, default=True)
    product_url = Column(String, nullable=False)
    last_updated = Column(String, nullable=False)

    product = relationship("ProductModel", back_populates="offers")

class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
