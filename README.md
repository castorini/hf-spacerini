# Spacerini 🦄

Spacerini is a modular framework for seamless building and deployment of interactive search applications, designed to facilitate the qualitative analysis of large scale research datasets.
In the current AI research landscape, billion-token textual corpora are widley used to pre-train large language models and conversational agents, which are then applied in a variety of downstream tasks.

Spacerini enables such qualitative analysis by leveraging and integrating features from both the Pyserini toolkit and the Hugging Face ecosystem. Users can easily index their collections and deploy them as ad-hoc search engines, making the retrieval of relevant data points quick and efficient. The user-friendly interface allows to search through massive datasets in no-code fashion, making Spacerini broadly accessible to anyone looking to qualitatively audit their text collections. Spacerini can also be leveraged by IR researchers aiming to demonstrate the capabilities of their indices in a simple and interactive way.

## Installation ⚒️

To get started create an access token with write access on huggingface to enable the creation of spaces. [Check here](https://huggingface.co/docs/hub/security-tokens) for documentation on user access tokens on huggingface.

Run `huggingface-cli login` to register your access token locally.

### Install from Github

- `pip install git+https://github.com/castorini/hf-spacerini.git`

### Dev Install

- Create a virual environment - `conda create --name spacerini`
- Clone the repository - `git clone https://github.com/castorini/hf-spacerini.git`
- Install in editable mode -`pip install -e ".[dev]"`

## Creating a simple application 🔎
You can deploy a search system for the test set of the Extreme Summatization [XSUM](https://huggingface.co/datasets/xsum) dataset on huggingface using the following command with variables stored in a [config.json](config.json): 
You can follow the instructions below to create .

```bash
spacerini --config-file config.json deploy
```
Voila!, you have successfully deployed a search engine on spaces 🤩🥳! 

## Prebuilt Spaces

- [MIRACL]() :

## Contribution 

## Acknowledgement
