import os
from datasets import Dataset, IterableDataset
from datasets import load_dataset
import pandas as pd
import ir_datasets
from typing import Generator, Dict, List

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

def load_ir_dataset_low_memory(dataset_name: str, num_proc: int) -> IterableDataset:
    """
    Load dataset from ir_datasets by streaming into a Dataset object. This is slower than first loading the data into a pandas DataFrame but does not require loading the entire ir_dataset into memory. This variant also supports multiprocessing if the data is sharded, and only consumes the generator once then caches it so that future calls are instantaneous.
    
    Parameters
    ----------
    dataset_name : str
        Name of dataset to load
    num_proc: int
        Number of processes to use
    
    Returns
    -------
    Dataset
    """
    return Dataset.from_generator(ir_dataset_dict_generator, gen_kwargs={"dataset_name": dataset_name}, num_proc=num_proc)

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

def load_from_hub(dataset_name_or_path: str, split: str, config_name: str=None, streaming: bool = True) -> Dataset:
    """
    Load dataset from HuggingFace Hub

    Parameters
    ----------
    dataset_name_or_path : str
        Name of dataset to load
    split : str
        Split of dataset to load
    streaming : bool
        Whether to load dataset in streaming mode
    
    Returns
    -------
    Dataset
    """

    return load_dataset(dataset_name_or_path, split=split, streaming=streaming, name=config_name)

def load_from_local(dataset_name_or_path: str or List[str], split: str, streaming: bool = True) -> Dataset:
    """
    Load dataset from local text file. Supports JSON, JSONL, CSV, and TSV.

    Parameters
    ----------
    dataset_name_or_path : str
        Path to a .json, .jsonl, .csv, or .tsv file
    streaming : bool
        Whether to load dataset in streaming mode
    
    Returns
    -------
    Dataset
    """
    if isinstance(dataset_name_or_path, str):
        assert os.path.exists(dataset_name_or_path), f"File {dataset_name_or_path} does not exist"
        if dataset_name_or_path.endswith(".jsonl") or dataset_name_or_path.endswith(".json"):
            return load_dataset("json", data_files=dataset_name_or_path, split=split, streaming=streaming)
        elif dataset_name_or_path.endswith(".csv"):
            return load_dataset("csv", data_files=dataset_name_or_path, split=split, streaming=streaming, sep=",")
        elif dataset_name_or_path.endswith(".tsv"):
            return load_dataset("csv", data_files=dataset_name_or_path, split=split, streaming=streaming, sep="\t")
        else:
            raise ValueError("Unsupported file type")

def load_from_sqlite_table(uri_or_con: str, table_or_query: str) -> Dataset:
    """
    Load dataset from a sqlite database table

    Parameters
    ----------
    uri_or_con : str
        URI to a SQLITE database or connection object
    table_or_query : str
        database table or query that returns a table
    
    Returns
    -------
    Dataset
    """
    return Dataset.from_sql(con=uri_or_con, sql=table_or_query)
