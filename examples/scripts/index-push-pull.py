from datasets import load_dataset
from spacerini.preprocess.utils import shard_dataset
from spacerini.index.index import index_json_shards
from spacerini.index.utils import push_index_to_hub, load_index_from_hub
from spacerini.search.utils import result_indices

DSET = "imdb"
SPLIT = "train"
COLUMN_TO_INDEX = "text"
NUM_PROC = 28
SHARDS_PATH = f"{DSET}-json-shards"
TEST_QUERY = "great movie"
NUM_RESULTS = 5
INDEX_PATH = "index"
DATASET_SLUG = "lucene-imdb-train"

dset = load_dataset(
    DSET,
    split=SPLIT
    )

shard_dataset(
    hf_dataset=dset,
    shard_size="10MB",
    column_to_index=COLUMN_TO_INDEX,
    shards_paths=SHARDS_PATH
    )

index_json_shards(
    shards_path=SHARDS_PATH,
    keep_shards=False,
    index_path= INDEX_PATH,
    language="en",
    n_threads=NUM_PROC
    )

print(
    f"First {NUM_RESULTS} results for query: \"{TEST_QUERY}\"",
    result_indices(TEST_QUERY, NUM_RESULTS, INDEX_PATH)
    )

push_index_to_hub(
    dataset_slug=DATASET_SLUG,
    index_path="index",
    delete_after_push=True
    )

new_index_path = load_index_from_hub(DATASET_SLUG)
print(
    f"First {NUM_RESULTS} results for query: \"{TEST_QUERY}\"",
    result_indices(TEST_QUERY, NUM_RESULTS, new_index_path)
    )