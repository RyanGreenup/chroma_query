serve:
    mkdir -p ./data
    uvx --from chromadb chroma run --path "./data/"

run:
    uv run python main.py

fmt:
    uv run black *.py

check: fmt
    uv run basedpyright *.py



get_example_docs:
    curl 'https://raw.githubusercontent.com/solidjs/solid-docs/cfae29e4b3f1616f65ad78736be58418676406c7/public/llms.txt' > example_docs/solid_llms.txt


example-query:
    uv run -- python main.py query "example_docs4" "signals and slots" --host localhost --port 8000
