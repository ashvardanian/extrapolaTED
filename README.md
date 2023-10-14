# ExtrapolaTED

> __Bringing TED experiences to every subject with Gen AI__

ExtrapolaTED is a tiny app, the produces a TED-like lectures on any given topic.
It uses:

- Wikipedia as a ground-truth retrieval source for textual and visual content.
- ChatGPT and Dall-E 3 for new produced content.

## Methodology

### Data

- [TED dataset](https://www.idiap.ch/en/dataset/ted).
  - [Data sheet on Zenodo](https://zenodo.org/records/4061423)
- [WIT dataset](https://github.com/google-research-datasets/wit):
  - [Data sheet on GitHub](https://github.com/google-research-datasets/wit/blob/main/DATA.md)

### Technology

- USearch: for retrieval
- UForm: for image embeddings
- ChatGPT: for story generation
- Dall-E 3 for image generation
- StreamLit: for UI


