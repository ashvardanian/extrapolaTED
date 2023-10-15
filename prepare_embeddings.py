import torch
import numpy as np
from uform import get_model
from torch import Tensor
from transformers import AutoTokenizer, AutoModel

# Check if CUDA is available and set the device accordingly
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model_uform = get_model("unum-cloud/uform-vl-english").to(device)
tokenizer_e5 = AutoTokenizer.from_pretrained("intfloat/e5-base-v2")
model_e5 = AutoModel.from_pretrained("intfloat/e5-base-v2").to(device)

# If multiple GPUs are available, wrap the model with DataParallel
if torch.cuda.device_count() > 1:
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


    if torch.cuda.device_count() > 1:
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
        batch_dict = model_uform.preprocess_image(input_texts_or_images)
        # Move data to the appropriate device
        batch_dict = {k: v.to(device) for k, v in batch_dict.items()}
        embeddings = model_uform.encode_image(batch_dict)
    
    return embeddings.detach().cpu().numpy().astype(np.float16)


if __name__ == "__main__":
    vectorize_e5(["test"] * 2048)
    # while True:
    #     vectorize_e5(["test"] * 2048)
    vectorize_uform(["test"] * 128)