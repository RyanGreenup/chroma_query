import json
from pathlib import Path
from typing import Sequence
import chromadb
from chromadb.types import Metadata
import uuid
from chromadb.api.types import QueryResult
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection, CollectionName
import requests
import markdownify


import typer

DEFAULT_CHUNK_SIZE = int(1000 * 4)  # ~1000 tokens

app = typer.Typer(
    pretty_exceptions_enable=False,
    context_settings={"help_option_names": ["-h", "--help"]}
)


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
    _ = create_collection(client, name)


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
        except Exception as e:
            print(f"{i}. {collection_name} (error accessing collection: {e})")
    
    # Print all collection info at once
    if info:
        print(json.dumps(info, indent=2))


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
                query_info = ""
                if 'metadatas' in results and results['metadatas'] is not None:
                    query_info = results['metadatas'][i]
                print(f"\nResults for query: {query_info}")
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


def fetch_and_convert_url(url: str) -> str:
    """
    Fetch content from a URL and convert HTML to markdown.
    
    Args:
        url: The URL to fetch content from
        
    Returns:
        Markdown text from the URL
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        html_content = response.text
        markdown_content = markdownify.markdownify(html_content)
        return markdown_content
    except Exception as e:
        raise ValueError(f"Error fetching or converting URL {url}: {e}")


@app.command()
def upload_url(
    collection_name: str,
    url: str,
    chunk_size: int = int(DEFAULT_CHUNK_SIZE),
    host: str = "localhost",
    port: int = 8000,
) -> None:
    """
    Upload content from a URL to a ChromaDB collection.
    
    Args:
        collection_name: Name of the collection to add content to
        url: URL to fetch content from
        chunk_size: Size of text chunks to split content into
        host: ChromaDB host
        port: ChromaDB port
    """
    client = chromadb.HttpClient(host, port)
    
    # Get or create collection
    if not collection_exists(client, collection_name):
        collection = create_collection(client, name=collection_name)
    else:
        collection = client.get_collection(collection_name)
    
    try:
        # Fetch and convert URL content
        print(f"Fetching content from {url}...")
        markdown_content = fetch_and_convert_url(url)
        
        # Skip empty content
        if not markdown_content.strip():
            print("URL returned empty content")
            return
            
        # Split into chunks
        chunks = chunk_text(markdown_content, chunk_size)
        
        # Generate unique IDs for each chunk
        ids = [str(uuid.uuid4()) for _ in range(len(chunks))]
        
        # Add metadata about the source
        metadatas: list[Metadata] = [
            {
                "source": url,
                "chunk_index": i,
                "total_chunks": len(chunks),
            }
            for i in range(len(chunks))
        ]
        
        # Add to collection
        collection.add(documents=chunks, ids=ids, metadatas=metadatas)
        
        print(f"Added {len(chunks)} chunks from {url} to collection '{collection_name}'")
        
    except Exception as e:
        print(f"Error processing URL: {e}")


# Import the default_docs module to make its commands available
from . import default_docs

# Add the default_docs commands as a subcommand group
app.add_typer(default_docs.app, name="defaults", help="Work with default documentation")

if __name__ == "__main__":
    app()
