from pyserini.search.lucene import LuceneSearcher

def result_indices(query: str, num_results: int, index_path: str, analyzer=None) -> list:
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

def result_page_iterator(hf_dataset: str, result_indices: list, results_per_page: int=10):
    """
    Iterate over the results of a query.
    Parameters
    ----------
    hf_dataset : str
        The path to the dataset or name of dataset on huggingface.
    result_indices : list
        The indices of the results.
    results_per_page : int (default=10)
        The number of results per page.
    
    Returns
    -------
    generator
        A generator that yields a pandas dataframe of results.
    """
    results = hf_dataset.select(result_indices)
    num_result_pages = int(len(results)/results_per_page) + 1
    for i in range(num_result_pages):
        yield results.shard(num_result_pages, i, contiguous=True).to_pandas()