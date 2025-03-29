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
    mkdir -p ./example_docs
    cd ./example_docs
    wget 'https://raw.githubusercontent.com/solidjs/solid-docs/cfae29e4b3f1616f65ad78736be58418676406c7/public/llms.txt'
