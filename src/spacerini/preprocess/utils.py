from typing import Union
from datasets import Dataset
from datasets.utils.py_utils import convert_file_size_to_int
import os

def shard_dataset(hf_dataset: Dataset, shard_size: Union[int, str], shards_paths: str, column_to_index: str) -> None: # TODO break this up into smaller functions
    """
    Shard a dataset into multiple files.
    Parameters
    ----------
    hf_dataset : datasets.Dataset
        a Hugging Face datasets object
    shard_size : str
        The size of each arrow shard that gets written as a JSON file.
    shards_paths : str
        The path to the directory where the shards will be stored.
    column_to_index : str
        The column to index mapping.
    
    Returns
    -------
    None
    """
    hf_dataset = hf_dataset.remove_columns([c for c in hf_dataset.column_names if c!=column_to_index])
    hf_dataset = hf_dataset.rename_column(column_to_index, "contents") # pyserini only wants a content column and an index column
    hf_dataset = hf_dataset.add_column("id", range(len(hf_dataset)))
    num_shards = get_num_shards(hf_dataset.data.nbytes, shard_size)
    os.makedirs(shards_paths, exist_ok=True)
    for shard_index in range(num_shards):
        shard = hf_dataset.shard(num_shards=num_shards, index=shard_index, contiguous=True)
        shard.to_json(f"{shards_paths}/docs-{shard_index:03d}.jsonl", orient="records", lines=True)

def get_num_shards(dataset_size: Union[int, str], max_shard_size: Union[int, str]) -> int:
    """
    Returns the number of shards required for a maximum shard size for a datasets.Dataset of a given size.
    Parameters
    ----------
    dataset_size: int or str
        The size of the dataset in either number of bytes or a string such as "10MB" or "6GB"
    max_shard_size: int or str
        The maximum size for every corresponding arrow shard in either number of bytes or a string such as "10MB" or "6GB".

    Returns
    -------
    int
    """
    max_shard_size = convert_file_size_to_int(max_shard_size)
    dataset_nbytes = convert_file_size_to_int(dataset_size)
    num_shards = int(dataset_nbytes / max_shard_size) + 1
    return max(num_shards, 1)