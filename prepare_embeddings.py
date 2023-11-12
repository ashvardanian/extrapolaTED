import os
import time

import torch
import numpy as np
from tqdm import tqdm
from uform import get_model
from torch import Tensor
from transformers import AutoTokenizer, AutoModel
from usearch.io import load_matrix, save_matrix

# Check if CUDA is available and set the device accordingly
allow_gpu = False
device = torch.device("cuda" if torch.cuda.is_available() and allow_gpu else "cpu")

model_uform = get_model("unum-cloud/uform-vl-english").to(device)
tokenizer_e5 = AutoTokenizer.from_pretrained("intfloat/e5-base-v2")
model_e5 = AutoModel.from_pretrained("intfloat/e5-base-v2").to(device)

# If multiple GPUs are available, wrap the model with DataParallel
if allow_gpu and torch.cuda.device_count() > 1:
    print(f"Using {torch.cuda.device_count()} GPUs!")
    model_e5 = torch.nn.DataParallel(model_e5)

scripted_model_e5 = model_e5


def average_pool(last_hidden_states: Tensor, attention_mask: Tensor) -> Tensor:
    last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
    return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]


def vectorize_e5(input_texts: list) -> np.ndarray:
    batch_dict = tokenizer_e5(
        input_texts,
        max_length=512,
        padding=True,
        truncation=True,
        return_tensors="pt",
    )
    # Move data to the appropriate device
    batch_dict = {k: v.to(device) for k, v in batch_dict.items()}

    def infer():
        outputs = scripted_model_e5(**batch_dict)
        embeddings = average_pool(outputs.last_hidden_state, batch_dict["attention_mask"])
        return embeddings.detach().cpu().numpy().astype(np.float16)


    if allow_gpu and torch.cuda.device_count() > 1:
        with torch.cuda.amp.autocast():
            return infer()
    else:
        return infer()


def vectorize_uform(input_texts_or_images: list) -> np.ndarray:

    if isinstance(input_texts_or_images[0], str):
        batch_dict = model_uform.preprocess_text(input_texts_or_images)
        # Move data to the appropriate device
        batch_dict = {k: v.to(device) for k, v in batch_dict.items()}
        embeddings = model_uform.encode_text(batch_dict)

    else:
        batch_dict = model_uform.preprocess_image(input_texts_or_images).to(device)
        embeddings = model_uform.encode_image(batch_dict)
    
    return embeddings.detach().cpu().numpy().astype(np.float16)


def vectorize_progressively(
    contents: list,
    vectorizer,      
    vectors_path: str
):
    if not os.path.exists(vectors_path):
        example = [contents[0]]
        example_vectors = vectorizer(example)
        vectors = np.zeros((len(contents), example_vectors.shape[1]), dtype=np.float32)
        save_matrix(vectors, vectors_path)
    else:
        vectors = load_matrix(vectors_path)

    batch_size = 128
    last_save_time = time.time()
    save_interval = 600  # 10 minutes in seconds

    zero_rows = np.any(vectors == 0, axis=1)
    zero_indices = np.where(zero_rows)[0]
    print(f"Will populate {len(zero_indices):,} of {len(contents):,}")

    # Using tqdm for progress bar. The "unit_scale" and "unit" arguments allow us to track samples/second.
    with tqdm(total=len(zero_indices), unit="samples") as pbar:
        for i in range(0, len(zero_indices), batch_size):
            batch_indices = zero_indices[i:i+batch_size]
            batch_texts = [contents[int(idx)] for idx in batch_indices]

            # Vectorize using vectorize_e5 function
            batch_vectors = vectorizer(batch_texts)

            # Update the vectors
            vectors[batch_indices] = batch_vectors

            # Update the progress bar
            pbar.update(len(batch_indices))

            # Check if it's time to save the progress
            current_time = time.time()
            if current_time - last_save_time > save_interval:
                save_matrix(vectors, vectors_path)
                last_save_time = current_time

    # Save the vectors after the entire loop is finished
    save_matrix(vectors, vectors_path)    


if __name__ == "__main__":
    vectorize_e5(["test"] * 2048)
    # while True:
    #     vectorize_e5(["test"] * 2048)
    vectorize_uform(["test"] * 128)