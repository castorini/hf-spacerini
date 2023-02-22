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
- pip install -e ".[dev]"

## Creating a simple application 🔎

You can follow the instructions below to create a search system for the test set of the Extreme Summatization [XSUM](https://huggingface.co/datasets/xsum) dataset on huggingface.

```python
import os
import logging
from spacerini.frontend import create_app, create_space_from_local
from spacerini.index import index_streaming_dataset

logging.basicConfig(level=logging.INFO)

DATASET = "xsum"
SPLIT = "test"
SPACE_TITLE = "XSum Dataset Search"
COLUMN_TO_INDEX = ["document"]
LOCAL_APP = "xsum-demo"
SDK = "gradio"
TEMPLATE = "gradio_roots_temp"
ORGANIZATION = "{update}"

cookiecutter_vars = {"dset_text_field": COLUMN_TO_INDEX, "space_title": SPACE_TITLE "local_app":LOCAL_APP,m"space_description": "This is a demo of Spacerini using the XSum dataset.", "dataset_name": "xsum"}

logging.info(f"Creating local app into {LOCAL_APP} directory")
create_app(template=TEMPLATE, extra_context_dict=cookiecutter_vars, output_dir="apps")

logging.info(f"Indexing {DATASET} dataset into {os.path.join('apps', LOCAL_APP, 'index')}")
index_streaming_dataset(
    dataset_name_or_path=DATASET,
    index_path= os.path.join("apps", LOCAL_APP, "index"),
    split=SPLIT,
    column_to_index=COLUMN_TO_INDEX,
    doc_id_column="id",
    storeContents=True,
    storeRaw=True,
    language="en"
)

logging.info(f"Creating space {SPACE_TITLE} on {ORGANIZATION}")
create_space_from_local(
    space_slug="xsum-test",
    organization=ORGANIZATION,
    space_sdk=SDK,
    local_dir=os.path.join("apps", LOCAL_APP),
    delete_after_push=False
    )
```
Voila!, you have successfully deployed a search engine on spaces 🤩🥳! 

## Prebuilt Spaces

- [MIRACL]() :

## Contribution 

## Acknowledgement
