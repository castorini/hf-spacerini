from spacerini.frontend.local import create_app
from spacerini.frontend.space import create_space_from_local
from datasets import load_dataset
from spacerini.preprocess.utils import shard_dataset
from spacerini.index.index import index_json_shards

DSET = "imdb"
local_app = "gradio_app"
sdk = "gradio"
cookiecutter_vars = {
                "hf_dataset": DSET,
                "hf_dataset_split": "train",
                "space_title":"IMDB search",
                "local_app":local_app
                }
create_app(template=sdk, extra_context_dict=cookiecutter_vars, output_dir=".")
dset = load_dataset(DSET, split="train")
shards_path = f"{DSET}-json-shards"
shard_dataset(hf_dataset=dset, shard_size="10MB", column_to_index="text", shards_paths=shards_path)
index_json_shards(shards_path=shards_path, index_path=local_app + "/index", language="en")
create_space_from_local(space_slug="imdb-search", space_sdk=sdk, local_dir=local_app, delete_after_push=False)