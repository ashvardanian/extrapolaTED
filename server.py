import os
import base64

from fastapi import FastAPI, HTTPException, Query
import pandas as pd
import numpy as np
import PIL
from io import BytesIO
from usearch.index import Index
from simsimd import cosine

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

def cluster_texts(query: str, nclusters: int = 10, npoints: int = 1000, abstracts: bool = False):

    # Vectorize the query
    query_vector = vectorize_e5([query])

    # Search in the indices
    arxiv_keys = arxiv_texts_index.search(query_vector[0], npoints).keys.flatten()
    arxiv_vecs = np.vstack(arxiv_texts_index.get(arxiv_keys))

    # Fetch abstracts using the keys
    points_titles = arxiv_texts_df.loc[arxiv_keys]["title"]
    points_abstracts = arxiv_texts_df.loc[arxiv_keys]["abstract"]

    centroids = np.random.choice(len(arxiv_keys), size=nclusters, replace=False)
    centroids = [int(x) for x in centroids]

    centroids_keys = arxiv_keys[centroids]
    centroids_vecs = arxiv_vecs[centroids]
    centroids_titles = points_titles.iloc[centroids]
    centroids_abstracts = points_abstracts.iloc[centroids]

    result_centroids = []
    result_points = []

    for i, key in enumerate(centroids_keys):
        result_centroids.append({
            "key": int(key),
            "title": str(centroids_titles.iloc[i]),
            "abstract": str(centroids_abstracts.iloc[i]) if abstracts else "",
            "distances": [
                cosine(centroids_vecs[i], centroids_vecs[j])
                for j in range(len(centroids))
            ],
        })

    for i, key in enumerate(arxiv_keys):
        result_points.append({
            "key": int(key),
            "title": str(points_titles.iloc[i]),
            "abstract": str(points_abstracts.iloc[i]) if abstracts else "",
            "distances": [
                cosine(arxiv_vecs[i], centroids_vecs[j])
                for j in range(len(centroids))                
            ],
        })

    return {
        "centroids": result_centroids,
        "points": result_points,
    }


@app.get("/search/")
async def search(query: str, top_k: int = 5):
    try:
        return try_one(query, top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/clusters/")
async def search(query: str, nclusters: int = 5, npoints: int = 1000, abstracts: bool = False):
    
    try:
        return cluster_texts(query, nclusters, npoints, abstracts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=33333)
    # print(cluster_texts("subgraph isomorphism"))

    