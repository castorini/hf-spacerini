# Spacerini 🦄

Spacerini is a modular framework for seamless building and deployment of interactive search application. It integrates Pyserini and the HuggingFace 🤗 ecosystem to enable facilitate the qualitative analysis of large scale research datasets. 

You can index collections and deploy them as ad-hoc search engines for efficient retrieval of relevant documents. 
Spacerini provides a customisable, user-friendly interface for auditing massive datasets. Spacerini also allows Information Retrieval (IR) researchers and Search Engineers to demonstrate the capabilities of their indices easily and interactively.  

Spacerini currently supports the use of Gradio and Streamlit to create these search applications. In the future, we will also support deployment of docker containers. 

## Installation ⚒️

To get started create an access token with write access on huggingface to enable the creation of spaces. [Check here](https://huggingface.co/docs/hub/security-tokens) for documentation on user access tokens on huggingface.

Run `huggingface-cli login` to register your access token locally.

### From Github

- `pip install git+https://github.com/castorini/hf-spacerini.git`

### Development Installation

You will need a development installation if you are contributing to Spacerini. 

- Create a virual environment - `conda create --name spacerini python=3.9`
- Clone the repository - `git clone https://github.com/castorini/hf-spacerini.git`
- Install in editable mode -`pip install -e ".[dev]"`


## Creating Spaces applications 🔎

Spacerini provides flexibility. You can customize every step of the `index-create-deploy` process as your project requires. You can provide your own index, built a more interactive web application and deploy changes as necessary.

Some of the commands that allow this flexibility are:

* index: Create a sparse, dense or hybrid index from specified dataset. This does not create a space.
* create-space: Create index from dataset and create HuggingFace Space application.
* deploy: Create HuggingFace Space application and deploy! 
* deploy-only: Deploy an already created or recently modified Space application.

If you have an existing index you have built, you can pass the `--index-exists` flag to any of the listed commands. Run `spacerini --help` for a full list of commands and arguments.

1. Getting started

You can deploy a search system for the test set of the Extreme Summatization  [XSUM](https://huggingface.co/datasets/xsum) dataset on huggingface using the following command. This system is based on our [gradio_roots_temp](templates/gradio_roots_temp/) template.

```bash
spacerini --from-example xsum deploy
```

Voila!, you have successfully deployed a search engine on HuggingFace Spaces 🤩🥳! This command downloads the XSUM dataset from the HuggingFace Hub, builds an interative user interface on top of a sparse index the dataset and deploys the application to HuggingFace Spaces. You can find the configurations for the application in: [examples/configs/xsum.json](examples/configs/xsum.json). 

2. Building your own custom application

The easiest way to build your own application is to provide a JSON configuration containing arguments for indexing, creating your space and deploying it. 

```bash
spacerini --config-file <path-to-config-file> <command-to-execute>
```
where `<command-to-execute>` may be `index`, `create-space`, `deploy` or `deploy-only`.

It helps to familiarise yourself with the arguments available for each step by running.

```bash
spacerini --help
```

If you are using a custom template you have built, you can pass it using the `template` argument. Once your application has been created locally, you can run it before deploying.

```bash
cd apps/<your-space-name>
python app.py
```

After completing all necessary modifications, run the following command to deploy your Spaces application

```bash
spacerini --config-file <path-to-config-file> deploy-only
```

## Contribution 

## Acknowledgement
