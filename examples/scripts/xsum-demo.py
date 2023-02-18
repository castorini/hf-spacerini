"""
This file contains a demo of Spacerini using Train Collection of the XSum dataset.
"""
from spacerini.frontend import create_app, create_space_from_local
from spacerini.index import index_json_shards, index_streaming_dataset


cookiecutter_vars = {
                "dset_text_field": COLUMN_TO_INDEX,
                "metadata_field": METADATA_COLUMNS[1],
                "space_title": SPACE_TITLE,
                "local_app":LOCAL_APP
                }