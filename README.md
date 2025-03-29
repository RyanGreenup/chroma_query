# ChromaDB Context Tool

A command-line tool for managing document collections in ChromaDB to provide relevant context for LLMs.

## Features

- Create, list, and delete ChromaDB collections
- Upload documents from directories
- Query collections for relevant text chunks
- Inject context directly into LLM prompts

## Requirements

- Python 3.8+
- ChromaDB server
- Dependencies: chromadb, typer, uuid

## Installation

```bash
# Install dependencies
uv install chromadb typer
```

## Usage

### Start ChromaDB Server

```bash
just serve
```

### Collection Management

```bash
# Create a collection
python main.py mk "collection_name"

# List all collections
python main.py ls

# Delete a collection
python main.py rm "collection_name"
```

### Document Operations

```bash
# Upload documents from a directory
python main.py upload "collection_name" ./docs_directory/

# Query a collection
python main.py query "collection_name" "your search query" --n-results 2

# Query with context injection
python main.py query "collection_name" "your search query" --inject
```

## How It Works

1. Documents are split into chunks of configurable size
2. Chunks are stored in ChromaDB with metadata
3. Semantic search finds relevant chunks for queries
4. Results can be displayed or injected as context

## Examples

See the `justfile` for example commands:

```bash
just example-create-collection
just example-upload-docs
just example-query-docs
```

## Development

```bash
# Format code
just fmt

# Type check
just check
```
