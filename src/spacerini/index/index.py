from itertools import chain
from typing import List
from typing import Literal

import shutil
from pyserini.index.lucene import LuceneIndexer
from pyserini.pyclass import autoclass
from datasets import load_dataset
from tqdm import tqdm
import json
import os


def parse_args(
    index_path: str,
    shards_path: str = "",
    fields: List[str] = None,
    language: str = None,
    pretokenized: bool = False,
    analyzeWithHuggingFaceTokenizer: str = None,
    storePositions: bool = True,
    storeDocvectors: bool = False,
    storeContents: bool = False,
    storeRaw: bool = False,
    keepStopwords: bool = False,
    stopwords: str = None,
    stemmer:  Literal["porter", "krovetz"] = None,
    optimize: bool = False,
    verbose: bool = False,
    quiet: bool = False,
    memory_buffer: str ="4096",
    n_threads: int = 5,
    **kwargs
):
    """
    Parse arguments into list for `SimpleIndexer` class in Anserini.
    
    Parameters
    ----------
        See io.anserini.IndexCollection.Args for argument definitions
        https://github.com/castorini/anserini

    Returns
    -------
    List of arguments to initialize the `LuceneIndexer`
    """
    params = locals()
    args = []
    args.extend([
        "-input", shards_path,
        "-threads", f"{n_threads}" if n_threads!=-1 else f"{os.cpu_count()}",
        "-collection", "JsonCollection",
        "-generator", "DefaultLuceneDocumentGenerator",
        "-index", index_path,
        "-memorybuffer", memory_buffer,
    ])
    variables = [
        "analyzeWithHuggingFaceTokenizer", "language", "stemmer"
    ]
    additional_args = [[f"-{var}", params[var]] for var in variables if params[var]]
    args.extend(chain.from_iterable(additional_args))

    if fields:
        args.extend(["-fields", " ".join(fields)])

    flags = [
        "pretokenized", "storePositions", "storeDocvectors", 
        "storeContents", "storeRaw", "optimize", "verbose", "quiet"
    ]
    args.extend([f"-{flag}" for flag in flags if params[flag]])
    
    return args


def index_json_shards(
    shards_path: str,
    index_path: str,
    keep_shards: bool = True,
    fields: List[str] = None,
    language: str = None,
    pretokenized: bool = False,
    analyzeWithHuggingFaceTokenizer: bool = None,
    storePositions: bool = True,
    storeDocvectors: bool = False,
    storeContents: bool = False,
    storeRaw: bool = False,
    keepStopwords: bool = False,
    stopwords: str = None,
    stemmer:  Literal["porter", "krovetz"] = None,
    optimize: bool = False,
    verbose: bool = False,
    quiet: bool = False,
    memory_buffer: str = "4096",
    n_threads: bool = -1,
):
    """Index dataset from a directory containing files

    Parameters
    ----------
    shards_path : str
        Path to dataset to index
    index_path : str
        Directory to store index
    keep_shards : bool
        If False, remove dataset after indexing is complete
    
    See io.anserini.IndexCollection.Args for remaining argument definitions
    https://github.com/castorini/anserini

    Returns
    -------
    None
    """
    args = parse_args(**locals())
    JIndexCollection = autoclass('io.anserini.index.IndexCollection')
    JIndexCollection.main(args)
    if not keep_shards:
        shutil.rmtree(shards_path)


def index_streaming_hf_dataset(
    index_path: str,
    ds_path: str,
    split: str,
    column_to_index: str,
    ds_config_name: str = None,   # For HF Dataset
    num_rows: int = None,
    disable_tqdm: bool = False,
    language: str = None,
    pretokenized: bool = False,
    analyzeWithHuggingFaceTokenizer: bool = None,
    storePositions: bool = True,
    storeDocvectors: bool = False,
    storeContents: bool = False,
    storeRaw: bool = False,
    keepStopwords: bool = False,
    stopwords: str = None,
    stemmer:  Literal["porter", "krovetz"] = None,
    optimize: bool = False,
    verbose: bool = False,
    quiet: bool = False,
    memory_buffer: str = "4096",
    n_threads: bool = 5,
):
    """Stream dataset from HuggingFace Hub & index

    Parameters
    ----------
    ds_path : str
        Name of HuggingFace dataset to stream
    split : str
        Split of dataset to index
    column_to_index : str
        Column of dataset to index
    ds_config_name: str
        Dataset configuration to stream. Usually a language name or code
    num_rows : str
        Number of rows in dataset
    disable_tqdm : bool
        Disable tqdm output
    
    See io.anserini.IndexCollection.Args for remaining argument definitions
    https://github.com/castorini/anserini

    Returns
    -------
    None
    """
    args = parse_args(**locals())
    ds = load_dataset(ds_path, name=ds_config_name, split=split, streaming=True)
    indexer = LuceneIndexer(args=args)
    for i, row in tqdm(enumerate(ds), total=num_rows, disable=disable_tqdm):
        indexer.add(json.dumps({"id": i, "contents": row[column_to_index]}))
    indexer.close()
