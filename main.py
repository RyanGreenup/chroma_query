import chromadb
from pprint import pprint
import pandas as pd
from typing import Any, List
from chromadb.api.types import QueryResult
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection


def initialize_chroma_client() -> ClientAPI:
    """Initialize and return a Chroma client."""
    return chromadb.Client()


def create_collection(client: ClientAPI, name: str) -> Collection:
    """Create a collection with the given name."""
    return client.create_collection(name=name)


def add_documents(collection: chromadb.Collection, documents: List[str], ids: List[str]) -> None:
    """Add documents to the specified collection."""
    collection.add(documents=documents, ids=ids)


def query_collection(
    collection: chromadb.Collection, query_texts: List[str], n_results: int
) -> QueryResult:
    """Query the collection with specific texts and return results."""
    return collection.query(query_texts=query_texts, n_results=n_results)


def convert_results_to_dataframe(results: QueryResult) -> pd.DataFrame:
    """Convert query results to a pandas DataFrame."""
    
    ids = results.get("ids", [])
    docs = results.get("documents", [])
    distances = results.get("distances", [])
    metadatas = results.get("metadatas", [])
    
    data = {
        "ids": [item for sublist in ids for item in sublist] if ids else [],
        "documents": [item for sublist in docs for item in sublist] if docs else [],
        "distances": [item for sublist in distances for item in sublist] if distances else [],
        "metadatas": [item for sublist in metadatas for item in sublist] if metadatas else [],
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
