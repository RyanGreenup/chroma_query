from pathlib import Path
import chromadb
from pprint import pprint
from chromadb.errors import UniqueConstraintError
from chromadb.types import Metadata
import pandas as pd
from tqdm import tqdm
import uuid
from chromadb.api.types import QueryResult
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection


import typer

app = typer.Typer(pretty_exceptions_enable=False)


def initialize_chroma_client() -> ClientAPI:
    """Initialize and return a Chroma client."""
    return chromadb.Client()


def create_collection(client: ClientAPI, name: str) -> Collection:
    """Create a collection with the given name."""
    return client.create_collection(name=name)


def add_documents(
    collection: chromadb.Collection, documents: list[str], ids: list[str]
) -> None:
    """Add documents to the specified collection."""
    collection.add(documents=documents, ids=ids)


def query_collection(
    collection: chromadb.Collection, query_texts: list[str], n_results: int
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
        "distances": (
            [item for sublist in distances for item in sublist] if distances else []
        ),
        "metadatas": (
            [item for sublist in metadatas for item in sublist] if metadatas else []
        ),
    }
    return pd.DataFrame(data)


def chunk_text(text: str, chunk_size: int = 2000) -> list[str]:
    """Split text into chunks of specified size."""
    print(text)
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


def load_documents_from_directory(
    collection: Collection, directory: Path, chunk_size: int = int(2000 / 4)
) -> None:
    """
    Walk over a directory, read files, split into chunks, and load into ChromaDB.

    Args:
        collection: ChromaDB collection to add documents to
        directory: Path to directory containing documents
    """
    if not directory.exists() or not directory.is_dir():
        raise ValueError(f"Directory {directory} does not exist or is not a directory")

    for file_path in directory.glob("**/*"):
        if file_path.is_file():
            try:
                # Read the file content
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Skip empty files
                if not content.strip():
                    continue

                # Split into chunks
                chunks = chunk_text(content, chunk_size)
                print(chunks)

                # Generate unique IDs for each chunk
                ids = [str(uuid.uuid4()) for _ in range(len(chunks))]

                # Add metadata about the source file
                metadatas: list[Metadata] = [
                    {
                        "source": str(file_path),
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                    }
                    for i in range(len(chunks))
                ]

                # Add to collection
                collection.add(documents=chunks, ids=ids, metadatas=metadatas)

                print(f"Added {len(chunks)} chunks from {file_path}")

            except Exception as e:
                print(f"Error processing file {file_path}: {e}")


@app.command()
def upload(
    collection_name: str,
    docs_dir: Path,
    chunk_size: int = int(2000 / 4),
    host: str = "localhost",
    port: int = 8000,
) -> None:
    """Upload documents from a directory to a ChromaDB collection."""
    client = chromadb.HttpClient(host, port)
    try:
        collection = create_collection(client, name=collection_name)
    except UniqueConstraintError as e:
        print(f"Warning: {collection_name} already exists, delete it first!")
        raise e

    # Load documents from the specified directory
    if docs_dir.exists() and docs_dir.is_dir():
        load_documents_from_directory(collection, docs_dir, chunk_size)
    else:
        print(f"Directory {docs_dir} not found")

    print(f"Documents uploaded to collection '{collection_name}'")

# Write a function to delete a collection AI!


@app.command()
def query(
    collection_name: str,
    query_text: str,
    n_results: int = 2,
    host: str = "localhost",
    port: int = 8000,
) -> None:
    """Query a ChromaDB collection with the specified text."""
    client = chromadb.HttpClient(host, port)

    # Get the existing collection
    try:
        collection = client.get_collection(name=collection_name)
    except ValueError:
        print(
            f"Collection '{collection_name}' not found. Please upload documents first."
        )
        return

    # Query the collection
    results = query_collection(collection, [query_text], n_results=n_results)

    # Display results
    df = convert_results_to_dataframe(results)
    pprint(df)


@app.command()
def list_collections(host: str, port: int) -> None:
    """List all available collections in the ChromaDB."""
    client = chromadb.HttpClient(host, port)
    collections = client.list_collections()

    if not collections:
        print("No collections found.")
        return

    print(f"Found {len(collections)} collections:")
    for i, collection_name in enumerate(collections, 1):
        try:
            # Get the collection to access its methods
            collection = client.get_collection(name=collection_name)
            doc_count = collection.count()
            print(f"{i}. {collection_name} (documents: {doc_count})")
        except Exception as e:
            print(f"{i}. {collection_name} (error accessing collection: {e})")


if __name__ == "__main__":
    app()
