import os
import numpy as np
import PIL

import pandas as pd
from tqdm import tqdm

from usearch.index import Index
from usearch.io import load_matrix

from prepare_embeddings import vectorize_e5, vectorize_uform
from prepare_embeddings import vectorize_progressively

df = pd.read_parquet("/home/shared_folder/wiki/meta_en.parquet")

# To export into our preferred Parquet format:
# df["abstract"] = df["caption"]
# df["title"] = df["caption"]
# df.pop("caption")
# df.to_parquet("./data/ann-wiki-images-3m/title_abstract.parquet")

vectors_path = "./data/ann-wiki-images-3m/abstract.e5-base-v2.fbin"
vectorize_progressively(df["caption"], vectorize_e5, vectors_path)

vectors_path = "./data/ann-wiki-images-3m/abstract.uform-vl-english.fbin"
vectorize_progressively(df["caption"], vectorize_uform, vectors_path)

def load_image_and_vectorize(paths):
    paths = [os.path.join("/home/shared_folder/wiki/", p) for p in paths]
    images = []
    for p in paths:
        try:
            images.append(PIL.Image.open(p))
        except (FileNotFoundError, PIL.UnidentifiedImageError):
            # assuming images are 256x256x3
            images.append(PIL.Image.fromarray(np.zeros((256, 256, 3), dtype=np.uint8))) 
    return vectorize_uform(images)

vectors_path = "./data/ann-wiki-images-3m/images.uform-vl-english.fbin"
vectorize_progressively(df["path"], load_image_and_vectorize, vectors_path)

vectors_path = "./data/ann-wiki-images-3m/abstract.e5-base-v2.fbin"
index_path = "./data/ann-wiki-images-3m/abstract.e5-base-v2.usearch"

vectors = load_matrix(vectors_path).astype(np.float16)
index = Index(dtype="f16", metric="cos", ndim=768)

if os.path.exists(index_path):
    index.load(index_path)
else:
    batch_size = 1000  # Adjust this based on your preference
    total_batches = int(np.ceil(vectors.shape[0] / batch_size))

    # Using tqdm for progress bar
    for i in tqdm(range(total_batches), desc="Indexing batches"):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, vectors.shape[0])

        batch_keys = np.arange(start_idx, end_idx)
        batch_vectors = vectors[start_idx:end_idx]

        index.add(batch_keys, batch_vectors)

    index.save(index_path)