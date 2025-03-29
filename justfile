serve:
    mkdir -p ./data
    uvx --from chromadb chroma run --path "./data/"

run:
    uv run python main.py

fmt:
    uv run black *.py

check: fmt
    uv run basedpyright *.py



example-fetch:
    curl 'https://raw.githubusercontent.com/solidjs/solid-docs/cfae29e4b3f1616f65ad78736be58418676406c7/public/llms.txt' > example_docs/solid_llms.txt

example-query:
    uv run -- python main.py query "example_docs4" "signals and slots" --host localhost --port 8000

    # uv run -- python main.py query "solid" 'signals' --n-results 5 --inject

example-create-collection:
    uv run -- python main.py mk "solidjs"

example-upload-docs:
    uv run -- python main.py upload "solid" ./example_docs/ --help

example-list-collections:
    uv run -- python main.py ls

example-query-docs:
    uv run -- python main.py query "solid" 'How can I pass a signal from one component out into the parent component?' --n-results 1 --inject

example-delete:
    uv run -- python main.py rm "solid"
