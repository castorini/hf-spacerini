"""
This file contains a demo of Spacerini using Train Collection of the XSum dataset.
"""
import os
import logging
from spacerini.frontend import create_app, create_space_from_local
from spacerini.index import index_streaming_dataset

logging.basicConfig(level=logging.INFO)

DATASET = "xsum"
SPLIT = "test"
SPACE_TITLE = "XSum Train Dataset Search"
COLUMN_TO_INDEX = ["document"]
LOCAL_APP = "xsum-demo"
SDK = "gradio"
TEMPLATE = "gradio_roots_temp"
ORGANIZATION = "ToluClassics"


cookiecutter_vars = {
                "dset_text_field": COLUMN_TO_INDEX,
                "space_title": SPACE_TITLE,
                "local_app":LOCAL_APP,
                "space_description": "This is a demo of Spacerini using the XSum dataset.",
                "dataset_name": "xsum"
                }



logging.info(f"Creating local app into {LOCAL_APP} directory")
create_app(
    template=TEMPLATE,
    extra_context_dict=cookiecutter_vars,
    output_dir="apps"
    )

logging.info(f"Indexing {DATASET} dataset into {os.path.join('apps', LOCAL_APP, 'index')}")
index_streaming_dataset(
    dataset_name_or_path=DATASET,
    index_path= os.path.join("apps", LOCAL_APP, "index"),
    split=SPLIT,
    column_to_index=COLUMN_TO_INDEX,
    doc_id_column="id",
    storeContents=True,
    storeRaw=True,
    language="en"
)

logging.info(f"Creating space {SPACE_TITLE} on {ORGANIZATION}")
create_space_from_local(
    space_slug="xsum-test",
    organization=ORGANIZATION,
    space_sdk=SDK,
    local_dir=os.path.join("apps", LOCAL_APP),
    delete_after_push=False
    )