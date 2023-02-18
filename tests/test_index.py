import os
import shutil
from os import path
import unittest
from spacerini.index import fetch_index_stats, index_streaming_dataset
from pyserini.search.lucene import LuceneSearcher
from typing import List


class TestIndex(unittest.TestCase):
    def setUp(self):
        self.index_path = path.join(path.dirname(__file__), "indexes")
        self.dataset_name_or_path = path.join(path.dirname(__file__),"data/sample_documents.jsonl")
        os.makedirs(self.index_path, exist_ok=True)


    def test_index_streaming_hf_dataset_local(self):
        """
        Test indexing a local dataset
        """
        local_index_path = path.join(self.index_path, "local")
        index_streaming_hf_dataset(
            index_path=local_index_path,
            dataset_name_or_path=self.dataset_name_or_path,
            split="train",
            column_to_index=["contents"],
            doc_id_column="id",
            language="en",
            storeContents = True,
            storeRaw = True,
            num_rows=3
        )
        
        self.assertTrue(os.path.exists(local_index_path))
        searcher = LuceneSearcher(local_index_path)
        
        hits = searcher.search('contents')
        self.assertTrue(isinstance(hits, List))
        self.assertEqual(hits[0].docid, 'doc1')
        self.assertEqual(hits[0].contents, "contents of doc one.")

        index_stats = fetch_index_stats(local_index_path)
        self.assertEqual(index_stats["total_terms"], 11)
        self.assertEqual(index_stats["documents"], 3)
        self.assertEqual(index_stats["unique_terms"], 9)

    
    def test_index_streaming_hf_dataset_huggingface(self):
        """
        Test indexing a dataset from HuggingFace Hub
        """
        hgf_index_path = path.join(self.index_path, "hgf")
        index_streaming_dataset(
            index_path=hgf_index_path,
            dataset_name_or_path="sciq",
            split="test",
            column_to_index=["question", "support"],
            language="en",
            num_rows=1000,
            storeContents = True,
            storeRaw = True
        )
        
        self.assertTrue(os.path.exists(hgf_index_path))
        searcher = LuceneSearcher(hgf_index_path)
        index_stats = fetch_index_stats(hgf_index_path)
        
        hits = searcher.search('contents')
        self.assertTrue(isinstance(hits, List))
        self.assertEqual(hits[0].docid, '528')
        self.assertEqual(index_stats["total_terms"], 54197)
        self.assertEqual(index_stats["documents"], 1000)
    
    def tearDown(self):
        shutil.rmtree(self.index_path)


        
