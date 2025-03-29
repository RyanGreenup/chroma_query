"""
Module for uploading default documentation from predefined URLs.
"""

import typer
from typing import List, Optional
from . import main


# Dictionary of default documentation URLs by collection
# See e.g. https://llmstxthub.com/
DEFAULT_DOCS = {
    "python": [
        "https://docs.python.org/3/tutorial/index.html",
        "https://docs.python.org/3/library/index.html",
    ],
    "data.sql.duckdb": ["https://duckdb.org/duckdb-docs.md"],
    "typer": ["https://typer.tiangolo.com/"],
    "chroma": ["https://docs.trychroma.com/"],
    "markdownify": ["https://markdownify.readthedocs.io/en/latest/"],
    "web.rest.rust.poem": [
        "https://raw.githubusercontent.com/poem-web/poem/refs/heads/master/examples/poem/hello-world/src/main.rs",
        "https://github.com/poem-web/poem/blob/master/examples/poem/middleware/src/main.rs",
        "https://docs.rs/poem-openapi/latest/poem_openapi/",
        "https://docs.rs/poem-openapi/latest/poem_openapi/#features",
    ],
    "web.components.daisy": [
        "https://daisyui.com/llms.txt",
    ],
    "web.components.ark": [
        "https://ark-ui.com/llms-full.txt",
    ],
    "web.framework.solid": [
        "https://raw.githubusercontent.com/solidjs/solid-docs/cfae29e4b3f1616f65ad78736be58418676406c7/public/llms.txt"
    ],
    "web.css.tailwind": [
        "https://tailwindcss.com/docs/font-variant-numeric",
        "https://tailwindcss.com/docs/align-content",
        "https://tailwindcss.com/docs/screens",
        "https://tailwindcss.com/docs/adding-custom-styles",
        "https://tailwindcss.com/docs/flex",
        "https://tailwindcss.com/docs/responsive-design",
        "https://tailwindcss.com/docs/grid-auto-rows",
        "https://tailwindcss.com/docs/grid-column",
        "https://tailwindcss.com/docs/space",
        "https://tailwindcss.com/docs/theme",
        "https://tailwindcss.com/docs/clear",
        "https://tailwindcss.com/docs/visibility",
        "https://tailwindcss.com/docs/z-index",
        "https://tailwindcss.com/docs/text-color",
        "https://tailwindcss.com/docs/flex-wrap",
        "https://tailwindcss.com/docs/min-height",
        "https://tailwindcss.com/docs/line-clamp",
        "https://tailwindcss.com/docs/using-with-preprocessors",
        "https://tailwindcss.com/docs/customizing-colors",
        "https://tailwindcss.com/docs/functions-and-directives",
        "https://tailwindcss.com/docs/height",
        "https://tailwindcss.com/docs/justify-content",
        "https://tailwindcss.com/docs/break-after",
        "https://tailwindcss.com/docs/optimizing-for-production",
        "https://tailwindcss.com/docs/text-decoration-thickness",
        "https://tailwindcss.com/docs/list-style-image",
        "https://tailwindcss.com/docs/break-before",
        "https://tailwindcss.com/docs/text-decoration-style",
        "https://tailwindcss.com/docs/gap",
        "https://tailwindcss.com/docs/place-self",
        "https://tailwindcss.com/docs/min-width",
        "https://tailwindcss.com/docs/flex-direction",
        "https://tailwindcss.com/docs/hover-focus-and-other-states",
        "https://tailwindcss.com/docs/grid-template-columns",
        "https://tailwindcss.com/docs/presets",
        "https://tailwindcss.com/docs/dark-mode",
        "https://tailwindcss.com/docs/place-content",
        "https://tailwindcss.com/docs/columns",
        "https://tailwindcss.com/docs/letter-spacing",
        "https://tailwindcss.com/docs/box-sizing",
        "https://tailwindcss.com/docs/object-position",
        "https://tailwindcss.com/docs/text-decoration",
        "https://tailwindcss.com/docs/align-self",
        "https://tailwindcss.com/docs/upgrade-guide",
        "https://tailwindcss.com/docs/display",
        "https://tailwindcss.com/docs/align-items",
        "https://tailwindcss.com/blog/2024-05-24-catalyst-application-layouts",
        "https://tailwindcss.com/docs/configuration",
        "https://tailwindcss.com/docs/preflight",
        "https://tailwindcss.com/docs/order",
        "https://tailwindcss.com/docs/float",
        "https://tailwindcss.com/docs/customizing-spacing",
        "https://tailwindcss.com/docs/text-transform",
        "https://tailwindcss.com/docs/reusing-styles",
        "https://tailwindcss.com/docs/plugins",
        "https://tailwindcss.com/docs/list-style-position",
        "https://tailwindcss.com/docs/size",
        "https://tailwindcss.com/docs/font-weight",
        "https://tailwindcss.com/docs/padding",
        "https://tailwindcss.com/docs/overscroll-behavior",
        "https://tailwindcss.com/docs/grid-row",
        "https://tailwindcss.com/docs/editor-setup",
        "https://tailwindcss.com/docs/grid-template-rows",
        "https://tailwindcss.com/docs/font-size",
        "https://tailwindcss.com/docs/margin",
        "https://tailwindcss.com/docs/font-style",
        "https://tailwindcss.com/showcase",
        "https://tailwindcss.com/docs/utility-first",
        "https://tailwindcss.com/docs/flex-basis",
        "https://tailwindcss.com/docs/grid-auto-flow",
        "https://tailwindcss.com/resources",
        "https://tailwindcss.com/docs/container",
        "https://tailwindcss.com/docs/break-inside",
        "https://tailwindcss.com/docs/text-decoration-color",
        "https://tailwindcss.com/docs/justify-self",
        "https://tailwindcss.com/docs/place-items",
        "https://tailwindcss.com/docs/flex-grow",
        "https://tailwindcss.com/docs/aspect-ratio",
        "https://tailwindcss.com/docs/flex-shrink",
        "https://tailwindcss.com/docs/list-style-type",
        "https://tailwindcss.com/docs/width",
        "https://tailwindcss.com/docs/box-decoration-break",
        "https://tailwindcss.com/docs/line-height",
        "https://tailwindcss.com/docs/grid-auto-columns",
        "https://tailwindcss.com/docs/text-underline-offset",
        "https://tailwindcss.com/docs/installation",
        "https://tailwindcss.com/docs/font-smoothing",
        "https://tailwindcss.com/docs/max-width",
        "https://tailwindcss.com/docs/position",
        "https://tailwindcss.com/docs/browser-support",
        "https://tailwindcss.com/",
        "https://tailwindcss.com/docs/overflow",
        "https://tailwindcss.com/blog",
        "https://tailwindcss.com/docs/object-fit",
        "https://tailwindcss.com/docs/justify-items",
        "https://tailwindcss.com/docs/text-align",
        "https://tailwindcss.com/docs/top-right-bottom-left",
        "https://tailwindcss.com/docs/content-configuration",
        "https://tailwindcss.com/docs/font-family",
        "https://tailwindcss.com/docs/isolation",
        "https://tailwindcss.com/docs/max-height",
    ],
}

app = typer.Typer(
    help="Upload default documentation from predefined URLs",
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.command()
def upload_defaults(
    collection_name: Optional[str] = None,
    urls: Optional[List[str]] = None,
    chunk_size: int = main.DEFAULT_CHUNK_SIZE,
    host: str = "localhost",
    port: int = 8000,
    all_collections: bool = False,
) -> None:
    """
    Upload content from default documentation URLs to ChromaDB collections.

    Args:
        collection_name: Name of the collection to add content to (must exist in DEFAULT_DOCS if urls not provided)
        urls: Optional list of URLs to fetch content from (uses defaults if None)
        chunk_size: Size of text chunks to split content into
        host: ChromaDB host
        port: ChromaDB port
        all_collections: If True, upload all default collections
    """
    if urls:
        # If URLs are provided, use them with the specified collection
        if not collection_name:
            print("Error: collection_name is required when providing custom URLs")
            return

        doc_urls = urls
        collections_to_process = {collection_name: doc_urls}

    elif all_collections:
        # Process all collections in DEFAULT_DOCS
        collections_to_process = DEFAULT_DOCS

    elif collection_name:
        # Process a single named collection from DEFAULT_DOCS
        if collection_name not in DEFAULT_DOCS:
            print(
                f"Error: Collection '{collection_name}' not found in default documentation."
            )
            print(f"Available collections: {', '.join(DEFAULT_DOCS.keys())}")
            return

        collections_to_process = {collection_name: DEFAULT_DOCS[collection_name]}

    else:
        # No valid options provided
        print(
            "Error: Please specify either collection_name, urls, or use --all-collections"
        )
        return

    # Process each collection
    for coll_name, doc_urls in collections_to_process.items():
        print(
            f"\nUploading documentation from {len(doc_urls)} URLs to collection '{coll_name}'..."
        )

        # Loop through each URL and upload its content
        for url in doc_urls:
            try:
                print(f"\nProcessing {url}...")
                main.upload_url(
                    collection_name=coll_name,
                    url=url,
                    chunk_size=chunk_size,
                    host=host,
                    port=port,
                )
            except Exception as e:
                print(f"Error processing {url}: {e}")
                continue

    print(f"\nFinished uploading default documentation")


@app.command()
def list_defaults() -> None:
    """List all available default documentation collections."""
    print("Available default documentation collections:")
    for collection_name, urls in DEFAULT_DOCS.items():
        print(f"\n{collection_name}:")
        for url in urls:
            print(f"  - {url}")


if __name__ == "__main__":
    app()
