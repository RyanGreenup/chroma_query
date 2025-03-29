import chromadb
from pprint import pprint
import pandas as pd
from typing import Any, Optional, list


def initialize_chroma_client():
    """Initialize and return a Chroma client."""
    return chromadb.Client()


def create_collection(client, name: str):
    """Create a collection with the given name."""
    return client.create_collection(name=name)


def add_documents(collection, documents: list[str], ids: list[str]) -> None:
    """Add documents to the specified collection."""
    collection.add(documents=documents, ids=ids)


def query_collection(
    collection, query_texts: list[str], n_results: int
) -> dict[str, Any]:
    """Query the collection with specific texts and return results."""
    return collection.query(query_texts=query_texts, n_results=n_results)


def convert_results_to_dataframe(results: dict[str, Any]) -> pd.DataFrame:
    """Convert query results to a pandas DataFrame."""
    data = {
        "ids": (
            [item for sublist in results.get("ids", []) for item in sublist]
            if results.get("ids")
            else []
        ),
        "documents": (
            [item for sublist in results.get("documents", []) for item in sublist]
            if results.get("documents")
            else []
        ),
        "distances": (
            [item for sublist in results.get("distances", []) for item in sublist]
            if results.get("distances")
            else []
        ),
        "metadatas": (
            [item for sublist in results.get("metadatas", []) for item in sublist]
            if results.get("metadatas")
            else []
        ),
    }
    return pd.DataFrame(data)


def main() -> None:
    client = initialize_chroma_client()
    collection = create_collection(client, name="my_collection")

    documents = ["A really fancy bar", "I took the dog for a walk", "I went to bed"]
    ids = ["id1", "id2", "id3"]
    add_documents(collection, documents, ids)

    query_texts = ["Pineapple in a bedroom"]
    results = query_collection(collection, query_texts, n_results=2)

    df = convert_results_to_dataframe(results)
    pprint(df)


if __name__ == "__main__":
    main()
