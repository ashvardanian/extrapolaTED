# extrapolaTED

> __Bringing TED experiences to every subject with Gen AI__

ExtrapolaTED is a tiny app, the produces a TED-like lectures on any given topic.
It uses:

- Wikipedia as a ground-truth retrieval source for textual and visual content.
- Arxiv paper abstracts as summaries of the most recent scientific achievements.
- ChatGPT and Dall-E 3 for new produced content.
- [ElevenLabs](https://elevenlabs.io) API to produce voice.
- [Wordware](https://wordware.ai) for multi-step API calls.

## Methodology

### Data

- [TED dataset](https://www.idiap.ch/en/dataset/ted) to understand which topics are already covered: __1 K transcripts__.
- [Arxiv abstracts - `unum-cloud/ann-arxiv-2m`](https://huggingface.co/datasets/unum-cloud/ann-arxiv-2m): __2 M vectorized abstracts__.
- [WIT - Wikipedia images dataset](https://github.com/google-research-datasets/wit) subset for image RAG: __3 M images__.
- [Wikipedia abstracts - `wikipedia`](https://huggingface.co/datasets/wikipedia/): __6 M abstracts__.

### Technology

- USearch: for retrieval.
- UForm: for image embeddings.
- ChatGPT: for story generation.
- Dall-E 3 for image generation.

To build up the Anaconda environment:

```sh
conda env create -f conda.yml
conda activate ExtrapolaTED
```

Or better manually, with PIP:

```sh
conda create -n extrapolated python=3.10
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip3 install -r requirements.txt
```

### Prompts

The entire prompt pipeline is hosted on Wordware.
You can clone and re-use it [here](https://app.wordware.ai/copy/25184ff7-db28-4c50-a0c4-2addbf31c28f).
