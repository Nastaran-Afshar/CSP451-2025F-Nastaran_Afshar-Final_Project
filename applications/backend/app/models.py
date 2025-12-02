from typing import List, Optional
from pydantic import BaseModel


# ---------- Products ----------

class Product(BaseModel):
    id: str
    name: str
    category: str
    price: float
    description: Optional[str] = None


# ---------- Cart ----------

class CartItemCreate(BaseModel):
    product_id: str
    quantity: int = 1


class CartItem(BaseModel):
    id: str
    user_id: str
    product_id: str
    quantity: int


# ---------- Orders ----------

class Order(BaseModel):
    id: str
    user_id: str
    items: List[CartItem]
    status: str
