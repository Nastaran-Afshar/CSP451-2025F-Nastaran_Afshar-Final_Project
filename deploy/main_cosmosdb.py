"""
Helper reference for Cosmos DB setup used by CloudMart.

This file is NOT the main FastAPI entrypoint; the API runs from app.main.
Use this only as documentation or for manual seeding if desired.
"""

from azure.cosmos import CosmosClient, PartitionKey
import os


COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")
COSMOS_DB_NAME = os.getenv("COSMOS_DB_NAME", "cloudmart")


def setup_cosmos():
    client = CosmosClient(COSMOS_ENDPOINT, credential=COSMOS_KEY)
    db = client.create_database_if_not_exists(id=COSMOS_DB_NAME)

    products = db.create_container_if_not_exists(
        id="products", partition_key=PartitionKey(path="/category")
    )
    cart = db.create_container_if_not_exists(
        id="cart", partition_key=PartitionKey(path="/user_id")
    )
    orders = db.create_container_if_not_exists(
        id="orders", partition_key=PartitionKey(path="/user_id")
    )

    # seed sample products
    sample_products = [
        {"id": "1", "name": "Laptop", "category": "Electronics", "price": 1299.99},
        {"id": "2", "name": "Headphones", "category": "Electronics", "price": 199.99},
        {"id": "3", "name": "Coffee Mug", "category": "Home", "price": 14.99},
        {"id": "4", "name": "Notebook", "category": "Office", "price": 7.49},
    ]
    for p in sample_products:
        products.upsert_item(p)


if __name__ == "__main__":
    setup_cosmos()
    print("Cosmos DB database and containers are ready with sample data.")
