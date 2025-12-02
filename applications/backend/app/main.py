import os
import uuid
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .models import Product, CartItemCreate, CartItem, Order
from .database import list_items, upsert_item, delete_item, get_container


# Demo user (no auth)
DEMO_USER_ID = "nmohammadiafshar"


app = FastAPI(title="CloudMart API")


# ---------- CORS (for frontend JS) ----------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for assignment demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Static frontend files ----------

STATIC_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend_static")
)

if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")



@app.get("/", response_class=FileResponse)
def serve_homepage():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=500, detail="Frontend files not found.")
    return index_path


# ---------- Health ----------

@app.get("/health")
def health():
    try:
        # simple query against products container
        _ = list_items("products", "SELECT TOP 1 * FROM c")
        return {"status": "ok", "cosmos": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "details": str(e)},
        )


# ---------- Products ----------

@app.get("/api/v1/products", response_model=List[Product])
def get_products(category: Optional[str] = None):
    if category:
        query = f"SELECT * FROM c WHERE c.category = '{category}'"
    else:
        query = "SELECT * FROM c"

    items = list_items("products", query)
    return items


@app.get("/api/v1/products/{product_id}", response_model=Product)
def get_product(product_id: str):
    query = f"SELECT * FROM c WHERE c.id = '{product_id}'"
    items = list_items("products", query)
    if not items:
        raise HTTPException(status_code=404, detail="Product not found")
    return items[0]


@app.get("/api/v1/categories", response_model=List[str])
def get_categories():
    query = "SELECT c.category FROM c"
    items = list_items("products", query)
    categories = sorted({item["category"] for item in items if "category" in item})
    return categories


# ---------- Cart ----------

@app.get("/api/v1/cart", response_model=List[CartItem])
def get_cart():
    query = f"SELECT * FROM c WHERE c.user_id = '{DEMO_USER_ID}'"
    items = list_items("cart", query)
    return items


@app.post("/api/v1/cart/items", response_model=CartItem)
def add_cart_item(payload: CartItemCreate):
    # confirm product exists
    product_query = f"SELECT * FROM c WHERE c.id = '{payload.product_id}'"
    products = list_items("products", product_query)
    if not products:
        raise HTTPException(status_code=400, detail="Invalid product_id")

    item_id = str(uuid.uuid4())
    item = {
        "id": item_id,
        "user_id": DEMO_USER_ID,
        "product_id": payload.product_id,
        "quantity": payload.quantity,
    }
    saved = upsert_item("cart", item)
    return saved


@app.delete("/api/v1/cart/items/{item_id}")
def delete_cart_item(item_id: str):
    # partition key = user_id
    delete_item("cart", item_id=item_id, partition_key=DEMO_USER_ID)
    return {"status": "deleted", "id": item_id}


# ---------- Orders ----------

@app.post("/api/v1/orders", response_model=Order)
def create_order():
    # get cart items for demo user
    query = f"SELECT * FROM c WHERE c.user_id = '{DEMO_USER_ID}'"
    cart_items = list_items("cart", query)

    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    order_id = str(uuid.uuid4())
    order = {
        "id": order_id,
        "user_id": DEMO_USER_ID,
        "items": cart_items,
        "status": "confirmed",
    }

    saved_order = upsert_item("orders", order)

    # clear cart after order
    for item in cart_items:
        delete_item("cart", item_id=item["id"], partition_key=DEMO_USER_ID)

    return saved_order


@app.get("/api/v1/orders", response_model=List[Order])
def list_orders():
    query = f"SELECT * FROM c WHERE c.user_id = '{DEMO_USER_ID}'"
    orders = list_items("orders", query)
    return orders
