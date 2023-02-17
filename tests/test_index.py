import os
import unittest
from spacerini.index import fetch_index_stats, index_streaming_hf_dataset
from pyserini.search.lucene import LuceneSearcher
from typing import List


class TestIndex(unittest.TestCase):
    def setUp(self):
        self.index_path = "tests/data/indexes"
        self.ds_path = "tests/data/sample_documents.jsonl"
        os.makedirs("tests/data/indexes", exist_ok=True)


    def test_index_streaming_hf_dataset(self):
        index_streaming_hf_dataset(
            index_path=self.index_path,
            ds_path=self.ds_path,
            split="test",
            column_to_index="contents",
            ds_config_name="sample_documents",
            language="en",
        )
        
        self.assertTrue(os.path.exists(self.index_path))
        searcher = LuceneSearcher(self.index_path)
        
        hits = searcher.search('contents')
        self.assertTrue(isinstance(hits, List))
        self.assertEqual(hits[0].id, 'doc1')
        self.assertEqual(hits[0].contents, "contents of doc one.")



    def test_fetch_index_stats(self, ):
        index_stats = fetch_index_stats(self.index_path)
        self.assertEqual(index_stats["total_terms"], 15)
        self.assertEqual(index_stats["documents"], 3)
        self.assertEqual(index_stats["unique_terms"], 10)
