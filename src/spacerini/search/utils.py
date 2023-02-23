from typing import List
from pyserini.search.lucene import LuceneSearcher
from datasets import Dataset

def result_indices(
        query: str,
        num_results: int,
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

    searcher = LuceneSearcher(index_path)
    if analyzer is not None:
        searcher.set_analyzer(analyzer)
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