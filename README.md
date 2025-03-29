# ChromaDB Context Tool

A command-line tool for managing document collections in ChromaDB to provide relevant context for LLMs.

This tool is used to inject context into LLMs and agents like Aider. It could also be used with

## Features

- Create, list, and delete ChromaDB collections
- Upload documents from directories
- Query collections for relevant text chunks
- Inject context directly into LLM prompts

## Requirements

- `uv`

## Installation and Usage

> [!NOTE]
> One can also install with:
> ```sh
> uv tool install --force git+https://github.com/ryangreenup/chroma_query
> ```

1. git clone
2. `just serve`
3. Make a collection
    3. `uv run -- python main.py mk my-docs`
4. Upload Docs
    3. `uv run -- python main.py upload my-docs /path/to/docs`
5. Query Docs
    3. `uv run -- python main.py query my-docs 'Some Search Term'`
6. Use from Aider. The default chunk size is 1000 tokens (ideal for embedding), so 2 results is 2000 tokens off the context window
    3. `/run uv run -- python main.py query my-docs 'Some Search Term' --n-results 2 --inject`

7. Make aliases whilst running a project

```
alias cs-ark="chroma-search --host localhost --port 8000 query 'web.components.ark' --n-results 2 --inject"
alias cs="chroma-search --host localhost --port 8000"
```


## Usage

### Collection Management

```bash
# Create a collection
python main.py mk "collection_name"

# List all collections
python main.py ls

# Delete a collection
python main.py rm "collection_name"
```


## How It Works

1. Documents are split into chunks of size `upload --chunk-size`
2. Chunks are stored in ChromaDB with metadata
3. Chroma's default semantic search finds relevant chunks for queries
4. Results can be injected into Aider

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

## Potetntial Improvements

- [Use Langchain](https://python.langchain.com/docs/integrations/document_loaders/unstructured_markdown/)
    - Big dependency that changes too often. Large context window solves the problem anyway.
- Automatically pull LLMs.txt
    - This would be convenient, e.g. the [SolidJS/llms.txt](https://raw.githubusercontent.com/solidjs/solid-docs/cfae29e4b3f1616f65ad78736be58418676406c7/public/llms.txt) or [DaisyUI/llms.txt](https://daisyui.com/docs/editor/)

- MCP Server
    - https://github.com/lutzleonhardt/mcpm-aider
    - Example MCP Servers
        - https://github.com/modelcontextprotocol/servers
        - https://github.com/modelcontextprotocol/servers/tree/main/src/everything
        - https://github.com/modelcontextprotocol/servers/tree/main/src/sqlite
    - Chroma MCP
        - https://github.com/chroma-core/chroma-mcp
            - https://docs.trychroma.com/docs/run-chroma/client-server
            - https://docs.trychroma.com/integrations/frameworks/anthropic-mcp#using-chroma-with-claude
    - MCP SDK (roll your own)
        - [Typesense MCP SDK](https://github.com/typesense/typesense-js)
        - [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk)
    - Zed MCP integration

        Write a simple plugin in Rust that runs the MCP server for Zed.

        - [Exemplar MCP Client Plugin](https://github.com/zed-extensions/postgres-context-server/blob/main/README.md?plain=1#L15)
        - [Exemplar MCP server for Postgres (configured to work with Zed Client)](https://github.com/zed-industries/postgres-context-server/blob/main/index.mjs)
        - [MCP Docs](https://zed.dev/docs/assistant/context-servers)

    - See Also
        - [Microsoft/markitdown MCP Server](https://github.com/microsoft/markitdown/tree/main/packages/markitdown-mcp)

- Switch to mxbai, see generally [^1743219892] [^1743219905]


[^1743219905]: https://ollama.com/blog/embedding-models

[^1743219892]: https://huggingface.co/spaces/mteb/leaderboard
