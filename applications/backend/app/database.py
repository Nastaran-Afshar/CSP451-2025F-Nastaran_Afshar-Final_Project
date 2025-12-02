import os
from typing import Any, Dict, List

from azure.cosmos import CosmosClient, PartitionKey


COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")
COSMOS_DB_NAME = os.getenv("COSMOS_DB_NAME", "cloudmart")


if not COSMOS_ENDPOINT or not COSMOS_KEY:
    raise RuntimeError(
        "COSMOS_ENDPOINT and COSMOS_KEY environment variables must be set."
    )

_client = CosmosClient(COSMOS_ENDPOINT, credential=COSMOS_KEY)
_database = _client.create_database_if_not_exists(id=COSMOS_DB_NAME)


def get_container(name: str):
    """
    Returns a Cosmos DB container object, creating it if not exists.
    products:   partition key = /category
    cart:       partition key = /user_id
    orders:     partition key = /user_id
    """
    if name == "products":
        pk = PartitionKey(path="/category")
    else:
        pk = PartitionKey(path="/user_id")

    return _database.create_container_if_not_exists(id=name, partition_key=pk)


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
