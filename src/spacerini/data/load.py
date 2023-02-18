import os
from datasets import Dataset, IterableDataset
from datasets import load_dataset
import pandas as pd
import ir_datasets
from typing import Generator, Dict, List
from huggingface_hub import HfApi


def ir_dataset_dict_generator(dataset_name: str) -> Generator[Dict,None,None]:
    """
    Generator for streaming datasets from ir_datasets
    https://github.com/allenai/ir_datasets
    Parameters
    ----------
    dataset_name : str
        Name of dataset to load
    """
    dataset = ir_datasets.load(dataset_name)
    for doc in dataset.docs_iter():
        yield {
            "contents": doc.text,
            "docid": doc.doc_id
            }

def load_ir_dataset(dataset_name: str) -> Dataset:
    """
    Load dataset from ir_datasets

    Parameters
    ----------
    dataset_name : str
        Name of dataset to load
    
    Returns
    -------
    Dataset
    """
    dataset = ir_datasets.load(dataset_name)
    return Dataset.from_pandas(pd.DataFrame(dataset.docs_iter()))

def load_ir_dataset_streaming(dataset_name: str) -> IterableDataset:
    """
    Load dataset from ir_datasets
    
    Parameters
    ----------
    dataset_name : str
        Name of dataset to load
    
    Returns
    -------
    IterableDataset
    """
    return IterableDataset.from_generator(ir_dataset_dict_generator, gen_kwargs={"dataset_name": dataset_name})

def load_from_pandas(df: pd.DataFrame) -> Dataset:
    """
    Load dataset from pandas DataFrame
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to load
    
    Returns
    -------
    Dataset
    """
    return Dataset.from_pandas(df)

def load_from_hub(dataset_name: str, split: str, config_name: str=None, streaming: bool = True) -> Dataset:
    """
    Load dataset from HuggingFace Hub

    Parameters
    ----------
    dataset_name : str
        Name of dataset to load
    split : str
        Split of dataset to load
    streaming : bool
        Whether to load dataset in streaming mode
    
    Returns
    -------
    Dataset
    """

    return load_dataset(dataset_name, split=split, streaming=streaming, name=config_name)



def load_from_local(dataset_name: str or List[str], split: str, streaming: bool = True) -> Dataset:
    """
    Load dataset from local JSONL file

    Parameters
    ----------
    path : str
        Path to JSONL file
    streaming : bool
        Whether to load dataset in streaming mode
    
    Returns
    -------
    Dataset
    """
    if isinstance(dataset_name, str):
        assert os.path.exists(dataset_name), f"File {dataset_name} does not exist"
        if dataset_name.endswith(".jsonl") or ds_path.endswith(".json"):
            return load_dataset("json", data_files=dataset_name, split=split, streaming=streaming)
        elif dataset_name.endswith(".csv"):
            return load_dataset("csv", data_files=dataset_name, split=split, streaming=streaming, sep=",")
        elif dataset_name.endswith(".tsv"):
            return load_dataset("csv", data_files=dataset_name, split=split, streaming=streaming, sep="\t")
        else:
            raise ValueError("Unsupported file type")

