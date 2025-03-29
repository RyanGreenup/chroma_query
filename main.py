import chromadb
from pprint import pprint
import pandas as pd
from typing import List, Dict


def initialize_chroma_client() -> chromadb.Client:
    """Initialize and return a Chroma client."""
    return chromadb.Client()


def create_collection(client: chromadb.Client, name: str) -> chromadb.Collection:
    """Create a collection with the given name."""
    return client.create_collection(name=name)


def add_documents(
    collection: chromadb.Collection, documents: List[str], ids: List[str]
) -> None:
    """Add documents to the specified collection."""
    collection.add(documents=documents, ids=ids)


def query_collection(
    collection: chromadb.Collection, query_texts: List[str], n_results: int
) -> Dict:
    """Query the collection with specific texts and return results."""
    return collection.query(query_texts=query_texts, n_results=n_results)


def convert_results_to_dataframe(results: Dict) -> pd.DataFrame:
    """Convert query results to a pandas DataFrame."""
    data = {
        "ids": [item for sublist in results["ids"] for item in sublist],
        "documents": [item for sublist in results["documents"] for item in sublist],
        "distances": [item for sublist in results["distances"] for item in sublist],
        "metadatas": [item for sublist in results["metadatas"] for item in sublist],
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
