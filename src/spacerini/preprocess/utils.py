from datasets.utils.py_utils import convert_file_size_to_int
import os

def shard_dataset(hf_dataset: str, shard_size: str, shards_paths: str, column_to_index: str) -> None: # TODO break this up into smaller functions
    """
    Shard a dataset into multiple files.
    Parameters
    ----------
    hf_dataset : str
        The path to the dataset or name of dataset on huggingface.
    shard_size : str
        The size of each shard.
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
    max_shard_size = convert_file_size_to_int(shard_size)
    dataset_nbytes = hf_dataset.data.nbytes
    num_shards = int(dataset_nbytes / max_shard_size) + 1
    num_shards = max(num_shards, 1)
    os.makedirs(shards_paths, exist_ok=True)
    for shard_index in range(num_shards):
        shard = hf_dataset.shard(num_shards=num_shards, index=shard_index, contiguous=True)
        shard.to_json(f"{shards_paths}/docs-{shard_index:03d}.jsonl", orient="records", lines=True)
