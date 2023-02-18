# Spacerini

Spacerini is a modular framework for seamless building and deployment of interactive search applications, designed to facilitate the qualitative analysis of large scale research datasets.
In the current AI research landscape, billion-token textual corpora are widley used to pre-train large language models and conversational agents, which are then applied in a variety of downstream tasks. However, as is clear from the instant community feedback and more principled research, the factuality and fairness of such models’ generations remain elusive as models tend to hallucinate facts and memorize rather then abstract knowledge. In order to understand their failure modes, researchers often turn to the training data in search for the source of questionable model predictions.

Spacerini enables such qualitative analysis by leveraging and integrating features from both the Pyserini toolkit and the Hugging Face ecosystem. Users can easily index their collections and deploy them as ad-hoc search engines, making the retrieval of relevant data points quick and efficient. The user-friendly interface allows to search through massive datasets in no-code fashion, making Spacerini broadly accessible to anyone looking to qualitatively audit their text collections. Spacerini can also be leveraged by IR researchers aiming to demonstrate the capabilities of their indices in a simple and interactive way.

## Installation

To get started create an access token with write access on huggingface to enable the creation of spaces. [Check here](https://huggingface.co/docs/hub/security-tokens) for documentation on user access tokens on huggingface.

Run `huggingface-cli login` to register your access token locally.

### Install from Pypi or Github

- `pip install spacerini` or for the latest updates  `pip install git+https://github.com/castorini/hf-spacerini.git`

### Dev Install

- Create a virual environment - `conda create --name spacerini`
- Clone the repository - `git clone https://github.com/castorini/hf-spacerini.git`
- pip install .

## Creating a simple application
```python
```
## Contribution 

## Acknowledgement