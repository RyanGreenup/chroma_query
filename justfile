serve:
    mkdir -p ./data
    uvx --from chromadb chroma run --path "./data/"

run:
    uv run python main.py
