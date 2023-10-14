# ExtrapolaTED

> __Bringing TED experiences to every subject with Gen AI__

ExtrapolaTED is a tiny app, the produces a TED-like lectures on any given topic.
It uses:

- Wikipedia as a ground-truth retrieval source for textual and visual content.
- ChatGPT and Dall-E 3 for new produced content.

## Methodology

### Data

- [TED dataset](https://www.idiap.ch/en/dataset/ted) to understand which topics are already covered, and in what style.
- [WIT - Wikipedia images dataset](https://github.com/google-research-datasets/wit) for image RAG.
- [Arxiv abstracts - `unum-cloud/ann-arxiv-2m`](https://huggingface.co/datasets/unum-cloud/ann-arxiv-2m) from HuggingFace.
- [Wikipedia abstracts - `wikipedia`](https://huggingface.co/datasets/wikipedia/) from HuggingFace.

### Technology

- USearch: for retrieval.
- UForm: for image embeddings.
- ChatGPT: for story generation.
- Dall-E 3 for image generation.
- StreamLit: for UI.


