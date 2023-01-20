from pyserini.search.lucene import LuceneSearcher

def result_indices(query, num_results, index_path, analyzer=None):
    searcher = LuceneSearcher(index_path)
    if analyzer is not None:
        searcher.set_analyzer(analyzer)
    hits = searcher.search(query, k=num_results)
    ix = [int(hit.docid) for hit in hits]
    return ix

def result_page_iterator(hf_dataset, result_indices, results_per_page=10):
    results = hf_dataset.select(result_indices)
    num_result_pages = int(len(results)/results_per_page) + 1
    for i in range(num_result_pages):
        yield results.shard(num_result_pages, i, contiguous=True).to_pandas()