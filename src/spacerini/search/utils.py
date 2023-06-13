from enum import Enum
from typing import Dict
from typing import List
from typing import Literal
from typing import Protocol
from typing import TypedDict
from typing import Union

from datasets import Dataset
from pyserini.analysis import get_lucene_analyzer
from pyserini.search import DenseSearchResult
from pyserini.search import JLuceneSearcherResult
from pyserini.search.faiss.__main__ import init_query_encoder
from pyserini.search.faiss import FaissSearcher
from pyserini.search.hybrid import HybridSearcher
from pyserini.search.lucene import LuceneSearcher

Encoder = Literal["dkrr", "dpr", "tct_colbert", "ance", "sentence", "contriever", "auto"]


class AnalyzerArgs(TypedDict):
    language: str
    stemming: bool
    stemmer: str
    stopwords: bool
    huggingFaceTokenizer: str


class Searcher(Protocol):
    def search(self, query: str, **kwargs) -> List[Union[DenseSearchResult, JLuceneSearcherResult]]:
        ...


def init_searcher(
    sparse_index_path: str = None,
    bm25_k1: float = None,
    bm25_b: float = None,
    analyzer_args: AnalyzerArgs = None,
    dense_index_path: str = None,
    encoder_name_or_path: str = None,
    encoder_class: Encoder = None, 
    tokenizer_name: str = None,
    device: str = None,
    prefix: str = None
) -> Union[FaissSearcher, HybridSearcher, LuceneSearcher]:
    """
    Initialize and return an approapriate searcher
    
    Parameters
    ----------
    sparse_index_path: str
        Path to sparse index
    dense_index_path: str
        Path to dense index
    encoder_name_or_path: str
        Path to query encoder checkpoint or encoder name
    encoder_class: str
        Query encoder class to use. If None, infer from `encoder`
    tokenizer_name: str
        Tokenizer name or path
    device: str
        Device to load Query encoder on. 
    prefix: str
        Query prefix if exists

    Returns
    -------
    Searcher: 
        A sparse, dense or hybrid searcher
    """
    if sparse_index_path:
        ssearcher = LuceneSearcher(sparse_index_path)
        if analyzer_args:
            analyzer = get_lucene_analyzer(**analyzer_args)
            ssearcher.set_analyzer(analyzer)
            if bm25_k1 and bm25_b:
                ssearcher.set_bm25(bm25_k1, bm25_b)

    if dense_index_path:
        encoder = init_query_encoder(
            encoder=encoder_name_or_path,
            encoder_class=encoder_class,
            tokenizer_name=tokenizer_name,
            topics_name=None,
            encoded_queries=None,
            device=device,
            prefix=prefix
        )

        dsearcher = FaissSearcher(dense_index_path, encoder)

        if sparse_index_path:
            hsearcher = HybridSearcher(dense_searcher=dsearcher, sparse_searcher=ssearcher)
            return hsearcher
        else:
            return dsearcher
    
    return ssearcher


def result_indices(
        query: str,
        num_results: int,
        searcher: Searcher,
        index_path: str,
        analyzer=None
        ) -> list:
    """
    Get the indices of the results of a query.
    Parameters
    ----------
    query : str
        The query.
    num_results : int
        The number of results to return.
    index_path : str
        The path to the index.
    analyzer : str (default=None)
        The analyzer to use.
    
    Returns
    -------
    list
        The indices of the returned documents.
    """
    # searcher.search()
    # searcher = LuceneSearcher(index_path)
    # if analyzer is not None:
    #     searcher.set_analyzer(analyzer)
    hits = searcher.search(query, k=num_results)
    ix = [int(hit.docid) for hit in hits]
    return ix


def result_page(
        hf_dataset: Dataset,
        result_indices: List[int],
        page: int = 0,
        results_per_page: int=10
        ) -> Dataset:
    """
    Returns a the ith results page as a datasets.Dataset object. Nothing is loaded into memory. Call `to_pandas()` on the returned Dataset to materialize the table.
    ----------
    hf_dataset : datasets.Dataset
        a Hugging Face datasets dataset.
    result_indices : list of int
        The indices of the results.
    page: int (default=0)
        The result page to return. Returns the first page by default.
    results_per_page : int (default=10)
        The number of results per page.
    
    Returns
    -------
    datasets.Dataset
        A results page.
    """
    results = hf_dataset.select(result_indices)
    num_result_pages = int(len(results)/results_per_page) + 1
    return results.shard(num_result_pages, page, contiguous=True)
