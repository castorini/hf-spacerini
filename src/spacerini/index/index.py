from itertools import chain
from typing import List
from typing import Literal

import shutil
from pyserini.index.lucene import LuceneIndexer, IndexReader
from typing import Any, Dict, List, Optional, Union
from pyserini.pyclass import autoclass
from tqdm import tqdm
import json
import os

from spacerini.data import load_from_hub, load_from_pandas, load_ir_dataset, load_ir_dataset_streaming, \
    load_from_local

"""
Descritiption of all the params used in this file
"""


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
    for_otf_indexing: bool = False,
    **kwargs
) -> List[str]:
    """
    Parse arguments into list for `SimpleIndexer` class in Anserini.
    
    Parameters
    ----------
    for_otf_indexing : bool
        If True, `-input` & `-collection` args are safely ignored.
        Used when performing on-the-fly indexing with HF Datasets.
    
    See [docs](docs/arguments.md) for remaining argument definitions

    Returns
    -------
    List of arguments to initialize the `LuceneIndexer`
    """
    params = locals()
    args = []
    args.extend([
        "-input", shards_path,
        "-collection", "JsonCollection",
        "-threads", f"{n_threads}" if n_threads!=-1 else f"{os.cpu_count()}",
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
    
    if for_otf_indexing:
        args = args[4:]
    return args


def index_json_shards(
    shards_path: str,
    index_path: str,
    keep_shards: bool = True,
    fields: List[str] = None,
    language: str = "en",
    pretokenized: bool = False,
    analyzeWithHuggingFaceTokenizer: str = None,
    storePositions: bool = True,
    storeDocvectors: bool = False,
    storeContents: bool = False,
    storeRaw: bool = False,
    keepStopwords: bool = False,
    stopwords: str = None,
    stemmer:  Literal["porter", "krovetz"] = "porter",
    optimize: bool = True,
    verbose: bool = False,
    quiet: bool = False,
    memory_buffer: str = "4096",
    n_threads: bool = 5,
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
    
    See [docs](../../docs/arguments.md) for remaining argument definitions

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
    column_to_index: List[str],
    doc_id_column: str = None,
    ds_config_name: str = None,   # For HF Dataset
    num_rows: int = -1,
    disable_tqdm: bool = False,
    language: str = "en",
    pretokenized: bool = False,
    analyzeWithHuggingFaceTokenizer: str = None,
    storePositions: bool = True,
    storeDocvectors: bool = False,
    storeContents: bool = False,
    storeRaw: bool = False,
    keepStopwords: bool = False,
    stopwords: str = None,
    stemmer:  Literal["porter", "krovetz"] = "porter",
    optimize: bool = True,
    verbose: bool = False,
    quiet: bool = True,
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
    column_to_index : List[str]
        Column of dataset to index
    doc_id_column : str
        Column of dataset to use as document ID
    ds_config_name: str
        Dataset configuration to stream. Usually a language name or code
    num_rows : int
        Number of rows in dataset
    
    See [docs](../../docs/arguments.md) for remaining argument definitions

    Returns
    -------
    None
    """
    
    args = parse_args(**locals(), for_otf_indexing=True)
    if os.path.exists(ds_path):
        ds = load_from_local(ds_path, split=split, streaming=True)
    else:
        ds = load_from_hub(ds_path, split=split,config_name=ds_config_name, streaming=True)

    indexer = LuceneIndexer(args=args)

    for i, row in tqdm(enumerate(ds), total=num_rows, disable=disable_tqdm):
        contents = " ".join([row[column] for column in column_to_index])
        indexer.add(json.dumps({"id": i if not doc_id_column else row[doc_id_column] , "contents": contents}))

    indexer.close()


def fetch_index_stats(index_path: str) -> Dict[str, Any]:
    """
    Fetch index statistics
    index_path : str
        Path to index directory
    Returns
    -------
    Dictionary of index statistics
    Dictionary Keys ==> total_terms, documents, unique_terms
    """
    assert os.path.exists(index_path), f"Index path {index_path} does not exist"
    index_reader = IndexReader(index_path)
    return index_reader.stats()