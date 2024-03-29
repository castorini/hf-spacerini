import json
from typing import List, Literal, Protocol, Tuple, TypedDict, Union

from pyserini.analysis import get_lucene_analyzer
from pyserini.index import IndexReader
from pyserini.search import DenseSearchResult, JLuceneSearcherResult
from pyserini.search.faiss.__main__ import init_query_encoder
from pyserini.search.faiss import FaissSearcher
from pyserini.search.hybrid import HybridSearcher
from pyserini.search.lucene import LuceneSearcher

EncoderClass = Literal["dkrr", "dpr", "tct_colbert", "ance", "sentence", "contriever", "auto"]


class AnalyzerArgs(TypedDict):
    language: str
    stemming: bool
    stemmer: str
    stopwords: bool
    huggingFaceTokenizer: str


class SearchResult(TypedDict):
    docid: str
    text: str
    score: float
    language: str


class Searcher(Protocol):
    def search(self, query: str, **kwargs) -> List[Union[DenseSearchResult, JLuceneSearcherResult]]:
        ...


def init_searcher_and_reader(
    sparse_index_path: str = None,
    bm25_k1: float = None,
    bm25_b: float = None,
    analyzer_args: AnalyzerArgs = None,
    dense_index_path: str = None,
    encoder_name_or_path: str = None,
    encoder_class: EncoderClass = None, 
    tokenizer_name: str = None,
    device: str = None,
    prefix: str = None
) -> Tuple[Union[FaissSearcher, HybridSearcher, LuceneSearcher], IndexReader]:
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
    Searcher: FaissSearcher | HybridSearcher | LuceneSearcher
        A sparse, dense or hybrid searcher
    """
    reader = None
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

        reader = IndexReader(sparse_index_path)
        dsearcher = FaissSearcher(dense_index_path, encoder)

        if sparse_index_path:
            hsearcher = HybridSearcher(dense_searcher=dsearcher, sparse_searcher=ssearcher)
            return hsearcher, reader
        else:
            return dsearcher, reader
    
    return ssearcher, reader


def _search(searcher: Searcher, reader: IndexReader, query: str, num_results: int = 10) -> List[SearchResult]:
    """
    Parameters:
    -----------
    searcher: FaissSearcher | HybridSearcher | LuceneSearcher
        A sparse, dense or hybrid searcher
    query: str
        Query for which to retrieve results
    num_results: int
        Maximum number of results to retrieve
    
    Returns:
    --------
    Dict:
    """
    def _get_dict(r: Union[DenseSearchResult, JLuceneSearcherResult]):
        if isinstance(r, JLuceneSearcherResult):
            return json.loads(r.raw)
        elif isinstance(r, DenseSearchResult):
            # Get document from sparse_index using index reader
            return json.loads(reader.doc(r.docid).raw())
    
    search_results = searcher.search(query, k=num_results)
    all_results = [
        SearchResult(
            docid=result["id"],
            text=result["contents"],
            score=search_results[idx].score   
        ) for idx, result in enumerate(map(lambda r: _get_dict(r), search_results))
    ]

    return all_results
