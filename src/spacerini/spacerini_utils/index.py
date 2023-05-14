import os
from typing import Any
from typing import Dict

from pyserini.index.lucene import IndexReader


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
