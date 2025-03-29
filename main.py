import json
from pathlib import Path
from typing import Sequence
import chromadb
from pprint import pprint
from chromadb.errors import UniqueConstraintError
from chromadb.types import Metadata
import pandas as pd
from tqdm import tqdm
import uuid
from chromadb.api.types import QueryResult
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection, CollectionName


import typer

DEFAULT_CHUNK_SIZE = int(1000 * 4)  # ~1000 tokens

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


def chunk_text(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE) -> list[str]:
    """Split text into chunks of specified size."""
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


def load_documents_from_directory(
    collection: Collection, directory: Path, chunk_size: int = int(DEFAULT_CHUNK_SIZE)
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


@app.command("mk")
def user_create_collection(name: str, host: str = "localhost", port: int = 8000):
    client = chromadb.HttpClient(host, port)
    create_collection(client, name)


def list_collections(client: ClientAPI) -> Sequence[CollectionName]:
    return client.list_collections()


@app.command("ls")
def user_list_collections(host: str = "localhost", port: int = 8000) -> None:
    """List all available collections in the ChromaDB."""
    client = chromadb.HttpClient(host, port)
    collections = list_collections(client)

    if not collections:
        print("No collections found.")
        return

    # pprint(collections)
    info = dict()

    for i, collection_name in enumerate(collections, 1):
        try:
            # Get the collection to access its methods
            collection = client.get_collection(name=collection_name)
            try:
                id = str(collection.id)
            except Exception as e:
                id = "ERROR: {e}"
            try:
                doc_count = collection.count()
            except Exception as e:
                doc_count = f"ERROR: {e}"
            info[id] = {"name": collection.name, "doc_count": doc_count}
            print(json.dumps(info, indent=2))
        except Exception as e:
            print(f"{i}. {collection_name} (error accessing collection: {e})")


def collection_exists(client: ClientAPI, collection_name: str) -> bool:
    collections = list_collections(client)
    return collection_name in collections


@app.command()
def upload(
    collection_name: str,
    docs_dir: Path,
    chunk_size: int = int(DEFAULT_CHUNK_SIZE),
    host: str = "localhost",
    port: int = 8000,
) -> None:
    """Upload documents from a directory to a ChromaDB collection."""
    client = chromadb.HttpClient(host, port)
    if not collection_exists(client, collection_name):
        collection = create_collection(client, name=collection_name)
    else:
        collection = client.get_collection(collection_name)

    # Load documents from the specified directory
    if docs_dir.exists() and docs_dir.is_dir():
        load_documents_from_directory(collection, docs_dir, chunk_size)
    else:
        print(f"Directory {docs_dir} not found")

    print(f"Documents uploaded to collection '{collection_name}'")


@app.command()
def query(
    collection_name: str,
    query_text: str,
    n_results: int = 2,
    host: str = "localhost",
    port: int = 8000,
    inject: bool = False,
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

    if not inject:
        # Display results
        print(json.dumps(results, indent=4))
    else:
        if docs := results.get("documents"):
            print(f"Found {len(docs[0])} results:")
            for i, chunks in enumerate(docs):
                print(
                    f"\nResults for query: {results['metadatas'][i] if 'metadatas' in results else ''}"
                )
                for j, chunk in enumerate(chunks):
                    print(f"\n--- Result {j+1} ---")
                    print(chunk)


@app.command("rm")
def delete_collection(
    collection_name: str,
    host: str = "localhost",
    port: int = 8000,
) -> None:
    """Delete a ChromaDB collection by name."""
    client = chromadb.HttpClient(host, port)

    try:
        client.delete_collection(name=collection_name)
        print(f"Collection '{collection_name}' has been deleted.")
    except ValueError:
        print(f"Collection '{collection_name}' not found.")
    except Exception as e:
        print(f"Error deleting collection '{collection_name}': {e}")


if __name__ == "__main__":
    app()
