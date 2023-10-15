from fastapi import FastAPI, HTTPException, Query
import pandas as pd
import numpy as np
from usearch.index import Index
from prepare_embeddings import vectorize_e5

arxiv_texts_index = Index.restore("./data/ann-arxiv-2m/abstract.e5-base-v2.usearch")
arxiv_text_df = pd.read_parquet("./data/ann-arxiv-2m/title_abstract.parquet")

wiki_texts_index = Index.restore("./data/ann-wiki-6m/abstract.e5-base-v2.usearch")
wiki_text_df = pd.read_parquet("./data/ann-wiki-6m/title_abstract.parquet")


app = FastAPI()


@app.get("/search/")
async def search(query: str, top_k: int = 5):
    try:
        # Vectorize the query
        query_vector = vectorize_e5([query])

        # Search in the indices
        arxiv_keys = arxiv_texts_index.search(query_vector[0], top_k).keys
        wiki_keys = wiki_texts_index.search(query_vector[0], top_k).keys

        # Fetch abstracts using the keys
        arxiv_abstracts = arxiv_text_df.loc[arxiv_keys.flatten()]["abstract"].tolist()
        wiki_abstracts = wiki_text_df.loc[wiki_keys.flatten()]["abstract"].tolist()

        return {
            "arxiv_abstracts": arxiv_abstracts,
            "wiki_abstracts": wiki_abstracts,
            "ted_transcript": "",
            "closest_image": "",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=33333)
