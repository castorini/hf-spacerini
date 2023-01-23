from pyserini.index.lucene import LuceneIndexer
from pyserini.pyclass import autoclass
from datasets import load_dataset
from tqdm import tqdm
import json

def index_json_shards(
    shards_path,
    index_path,
    keep_shards,

    ):
    JIndexCollection = autoclass('io.anserini.index.IndexCollection')
    JIndexCollection.main()
# !python -m pyserini.index.lucene \
#   --collection JsonCollection \
#   --input to_index_json/ \
#   --index indexes/default_analyzer \
#   --generator DefaultLuceneDocumentGenerator \
#   --threads 20 \
#   --storePositions --storeDocvectors

def index_streaming_hf_dataset(
    ds_path,
    split,
    index_path,
    column_to_index,
    num_rows=None,
    disable_tqdm=False
    ):
    ds = load_dataset(ds_path, split=split, streaming=True)
    indexer = LuceneIndexer(index_path)
    for i, row in tqdm(enumerate(ds), total=num_rows, disable=disable_tqdm):
        indexer.add(json.dumps({"id": i,"contents": row[column_to_index]}))
    indexer.close()