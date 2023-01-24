from pyserini.index.lucene import LuceneIndexer
from pyserini.pyclass import autoclass
from datasets import load_dataset
from tqdm import tqdm
import json
import os

def index_json_shards(
    shards_path,
    index_path,
    fields=[],
    language="en",
    store_positions=True,
    store_docvectors=False,
    store_contents=False,
    store_raw=False,
    optimize=False,
    keep_shards=False,
    verbose=False,
    quiet=False,
    n_threads=-1,
    ):
# "-verbose"
# "-quiet"
# "-index"
# "-fields"
# "-storePositions"
# "-storeDocvectors"
# "-storeContents"
# "-storeRaw"
# "-optimize"
# "-keepStopwords"
# "-stopwords"
# "-stemmer"
# "-memorybuffer"
# "-language"
# "-pretokenized"
# "-analyzeWithHuggingFaceTokenizer"
    args = []
    args.extend(["-input", shards_path,
                "-threads", n_threads if n_threads!=-1 else os.cpu_count(),
                "-collection", "JsonCollection",
                "-generator", "DefaultLuceneDocumentGenerator"],
                "-index", index_path)
    JIndexCollection = autoclass('io.anserini.index.IndexCollection')
    JIndexCollection.main(args)


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