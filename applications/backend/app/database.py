import os
from typing import Any, Dict, List
from ~/docker/docker-compose.yml import COSMOS_DB_NAME, COSMOS_KEY, COSMOS_ENDPOINT

from azure.cosmos import CosmosClient, PartitionKey


# --------- Config from environment ---------

COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")
COSMOS_DB_NAME = os.getenv("COSMOS_DB_NAME", "cloudmart")

if not COSMOS_ENDPOINT or not COSMOS_KEY or COSMOS_ENDPOINT == "..." or COSMOS_KEY == "...":
    raise RuntimeError(
        "COSMOS_ENDPOINT and COSMOS_KEY environment variables must be set to valid values "
        "and must not be '...'."
    )

# Create client & database if they don't exist
_client = CosmosClient(COSMOS_ENDPOINT, credential=COSMOS_KEY)
_database = _client.create_database_if_not_exists(id=COSMOS_DB_NAME)


# --------- Container helpers ---------

def get_container(name: str):
    """
    Returns a Cosmos DB container object, creating it if not exists.

    products: partition key = /category
    cart:     partition key = /user_id
    orders:   partition key = /user_id
    """
    if name == "products":
        pk = PartitionKey(path="/category")
    else:
        pk = PartitionKey(path="/user_id")

    return _database.create_container_if_not_exists(id=name, partition_key=pk)


def _seed_products_if_empty() -> None:
    """
    Seed the products container with sample data if the container is empty.
    """
    container = get_container("products")
    # Check if there are any items at all
    items = list(
        container.query_items(
            query="SELECT TOP 1 * FROM c",
            enable_cross_partition_query=True,
        )
    )
    if items:
        # Already seeded, nothing to do
        return

    sample_products = [
        {"id": "1", "name": "Laptop", "category": "Electronics", "price": 1299.99},
        {"id": "2", "name": "Headphones", "category": "Electronics", "price": 199.99},
        {"id": "3", "name": "Coffee Mug", "category": "Home", "price": 14.99},
        {"id": "4", "name": "Notebook", "category": "Office", "price": 7.49},
    ]
    for p in sample_products:
        container.upsert_item(p)


def _initialize_db() -> None:
    """
    Ensure all required containers exist and seed products.

    After this runs you will see in Data Explorer:
      - products  (pk: /category)
      - cart      (pk: /user_id)
      - orders    (pk: /user_id)
    """
    get_container("products")
    get_container("cart")
    get_container("orders")
    _seed_products_if_empty()


# Run initialization once when the module is imported
_initialize_db()


# --------- Public CRUD functions used by main.py ---------

def list_items(container_name: str, query: str) -> List[Dict[str, Any]]:
    container = get_container(container_name)
    return list(
        container.query_items(
            query=query,
            enable_cross_partition_query=True,
        )
    )


def upsert_item(container_name: str, item: Dict[str, Any]) -> Dict[str, Any]:
    container = get_container(container_name)
    return container.upsert_item(item)


def delete_item(container_name: str, item_id: str, partition_key: str) -> None:
    container = get_container(container_name)
    container.delete_item(item=item_id, partition_key=partition_key)
