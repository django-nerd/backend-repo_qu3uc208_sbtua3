"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import date

# Example schemas (you can keep or remove later)
class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Pickleball Venue Schemas

class Court(BaseModel):
    name: str
    surface: Optional[str] = None
    indoor: bool = False

class Booking(BaseModel):
    booking_date: date = Field(..., description="Booking date (YYYY-MM-DD)")
    time_slot: str = Field(..., description="Time slot label, e.g., 07:00-08:00")
    court_id: str = Field(..., description="Court identifier")
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    notes: Optional[str] = None
    players: Optional[int] = Field(2, ge=1, le=4)

class ContactMessage(BaseModel):
    full_name: str
    email: EmailStr
    subject: str
    message: str
    phone: Optional[str] = None

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
