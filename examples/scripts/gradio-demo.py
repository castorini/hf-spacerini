from spacerini.frontend.local import create_app
from spacerini.frontend.space import create_space_from_local
from datasets import load_dataset
from spacerini.preprocess.utils import shard_dataset, get_num_shards
from spacerini.index.index import index_json_shards

DSET = "imdb"
SPLIT = "train"
SPACE_TITLE = "IMDB search"
COLUMN_TO_INDEX = "text"
METADATA_COLUMNS = ["sentiment", "docid"]
NUM_PROC = 28
SHARDS_PATH = f"{DSET}-json-shards"
LOCAL_APP = "gradio_app"
SDK = "gradio"
ORGANIZATION = "cakiki"
MAX_ARROW_SHARD_SIZE="1GB"

cookiecutter_vars = {
                "dset_text_field": COLUMN_TO_INDEX,
                "metadata_field": METADATA_COLUMNS[1],
                "space_title": SPACE_TITLE,
                "local_app":LOCAL_APP
                }
create_app(
    template=SDK,
    extra_context_dict=cookiecutter_vars,
    output_dir="."
    )

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
    index_path=LOCAL_APP + "/index",
    language="en",
    n_threads=NUM_PROC
    )

dset = dset.add_column("docid", range(len(dset)))
num_shards = get_num_shards(dset.data.nbytes, MAX_ARROW_SHARD_SIZE)
dset.remove_columns([c for c in dset.column_names if not c in [COLUMN_TO_INDEX,*METADATA_COLUMNS]]).save_to_disk(
    LOCAL_APP + "/data",
    num_shards=num_shards,
    num_proc=NUM_PROC
    )

create_space_from_local(
    space_slug="imdb-search",
    organization=ORGANIZATION,
    space_sdk=SDK,
    local_dir=LOCAL_APP,
    delete_after_push=False
    )