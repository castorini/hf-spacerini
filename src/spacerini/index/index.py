import shutil
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
    language=None,
    pretokenized=False,
    hf_tokenizer=None,
    store_positions=True,
    store_docvectors=False,
    store_contents=False,
    store_raw=False,
    optimize=False,
    keep_shards=True,
    verbose=False,
    quiet=False,
    memory_buffer="4096",
    n_threads=-1,
    ):
# LEFT TO ADD:
# "-keepStopwords"
# "-stopwords"
# "-stemmer"
    args = []
    args.extend(["-input", shards_path,
                "-threads", f"{n_threads}" if n_threads!=-1 else f"{os.cpu_count()}",
                "-collection", "JsonCollection",
                "-generator", "DefaultLuceneDocumentGenerator",
                "-index", index_path,
                "-memorybuffer", memory_buffer])
    if pretokenized:
        args.append("-pretokenized")
    if hf_tokenizer:
        args.extend(["-analyzeWithHuggingFaceTokenizer", hf_tokenizer])
    if store_positions:
        args.append("-storePositions")
    if store_docvectors:
        args.append("-storeDocvectors")
    if store_contents:
        args.append("-storeContents")
    if store_raw:
        args.append("-storeRaw")
    if optimize:
        args.append("-optimize")
    if verbose:
        args.append("-verbose")
    if quiet:
        args.append("-quiet")
    if fields:
        args.extend(["-fields", " ".join(fields)])
    if language:
        args.extend(["-language", language])
    JIndexCollection = autoclass('io.anserini.index.IndexCollection')
    JIndexCollection.main(args)
    if not keep_shards:
        shutil.rmtree(shards_path)

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