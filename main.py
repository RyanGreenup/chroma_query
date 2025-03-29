import chromadb
from pprint import pprint

# NOTE consider changing the client, see e.g.
# https://huggingface.co/spaces/mteb/leaderboard

def main():
    chroma_client = chromadb.Client()
    collection = chroma_client.create_collection(name="my_collection")

    collection.add(
        documents=[
            "A really fancy bar",
            "I took the dog for a walk",
            "I went to bed",
        ],
        ids=["id1", "id2", "id3"]
    )
    results = collection.query(
        query_texts=["Pineapple in a bedroom"], # Chroma will embed this for you
        n_results=2 # how many results to return
    )

    import pandas as pd
    
    data = {
            'ids': [item for sublist in results['ids'] for item in sublist],
            'documents': [item for sublist in results['documents'] for item in sublist],
            'distances': [item for sublist in results['distances'] for item in sublist],
            'metadatas': [item for sublist in results['metadatas'] for item in sublist]
        }
        
    df = pd.DataFrame(data)
    pprint(df)

if __name__ == "__main__":
    main()
