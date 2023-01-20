from datasets import load_dataset
from datasets.utils.py_utils import convert_file_size_to_int
import os

def prepare_dataset(ds_path, split, shard_size, shards_paths, column_to_index): # TODO break this up into smaller functions
    ds = load_dataset(ds_path, split=split)
    ds = ds.remove_columns([c for c in ds.columns if c!=column_to_index])
    ds.rename_column(column_to_index, "contents") # pyserini only wants a content column and an index column
    max_shard_size = convert_file_size_to_int(shard_size)
    dataset_nbytes = ds.data.nbytes
    num_shards = int(dataset_nbytes / max_shard_size) + 1
    num_shards = max(num_shards, 1)
    os.makedirs(shards_paths, exist_ok=True)
    for shard_index in range(num_shards):
        shard = ds.shard(num_shards=num_shards, index=shard_index, contiguous=True)
        shard.to_json(f"to_index_json/docs-{shard_index:03d}.jsonl", orient="records", lines=True)