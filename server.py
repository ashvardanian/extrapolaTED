import os
import base64

from fastapi import FastAPI, HTTPException, Query
import pandas as pd
import numpy as np
import PIL
from io import BytesIO
from usearch.index import Index

from prepare_embeddings import vectorize_e5

arxiv_texts_index = Index.restore("./data/ann-arxiv-2m/abstract.e5-base-v2.usearch")
arxiv_texts_df = pd.read_parquet("./data/ann-arxiv-2m/title_abstract.parquet")

wiki_texts_index = Index.restore("./data/ann-wiki-6m/abstract.e5-base-v2.usearch")
wiki_texts_df = pd.read_parquet("./data/ann-wiki-6m/title_abstract.parquet")

wiki_images_index = Index.restore("./data/ann-wiki-images-3m/abstract.e5-base-v2.usearch")
wiki_images_df = pd.read_parquet("./data/ann-wiki-images-3m/title_abstract.parquet")


app = FastAPI()

def try_one(query: str, top_k: int = 5):
    # Vectorize the query
    query_vector = vectorize_e5([query])

    # Search in the indices
    arxiv_texts_keys = arxiv_texts_index.search(query_vector[0], top_k).keys
    wiki_texts_keys = wiki_texts_index.search(query_vector[0], top_k).keys
    wiki_images_keys = wiki_images_index.search(query_vector[0], top_k).keys

    # Fetch abstracts using the keys
    arxiv_texts = arxiv_texts_df.loc[arxiv_texts_keys.flatten()]["abstract"].tolist()
    wiki_texts = wiki_texts_df.loc[wiki_texts_keys.flatten()]["abstract"].tolist()
    wiki_images_paths = wiki_images_df.loc[wiki_images_keys.flatten()]["path"].tolist()
    wiki_images_captions = wiki_images_df.loc[wiki_images_keys.flatten()]["abstract"].tolist()

    wiki_images = []
    for path, caption in zip(wiki_images_paths, wiki_images_captions):
        try:
            path = os.path.join("/home/shared_folder/wiki/", path)
            image = PIL.Image.open(path)
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            wiki_images.append({
                "text": caption,
                "image": f"data:image/jpeg;base64,{img_str}",
            })
        except Exception as e:
            print(f"Error image processing: ", e)

    return {
        "arxiv_texts": arxiv_texts,
        "wiki_texts": wiki_texts,
        "images": wiki_images,
    }


@app.get("/search/")
async def search(query: str, top_k: int = 5):
    try:
        return try_one(query, top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=33333)
    # print(try_one("subgraph isomorphism"))