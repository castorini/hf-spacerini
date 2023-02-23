import argparse
import json
import logging
import os
from pathlib import Path

from spacerini.frontend import create_app, create_space_from_local
from spacerini.index import index_streaming_dataset


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="Spacerini",
        description="A modular framework for seamless building and deployment of interactive search applications.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="Written by: Akintunde 'theyorubayesian' Oladipo <akin.o.oladipo@gmail.com>, Christopher Akiki <christopher.akiki@gmail.com>, Odunayo Ogundepo <ogundepoodunayo@gmail.com>"
    )
    parser.add_argument("--config-file", type=str, help="Path to configuration for space")
    parser.add_argument("--verbose", type=bool, default=True, help="If True, print verbose output")

    sub_parser = parser.add_subparsers(dest="command", title="Commands", description="Valid commands")
    index_parser = sub_parser.add_parser("index", help="Index dataset. This will not create the app or deploy it.")
    create_parser = sub_parser.add_parser("create-space", help="Create space in local directory. This won't deploy the space.")
    deploy_parser = sub_parser.add_parser("deploy", help="Deploy new space.")
    deploy_parser.add_argument("--delete-after", type=bool, default=False, help="If True, delete the local directory after pushing it to the Hub.")

    space_args = deploy_parser.add_argument_group("Space arguments")
    space_args.add_argument("--space-name", required=False)
    space_args.add_argument("--space-title", required=False, help="Title to show on Space")
    space_args.add_argument("--space-url-slug", required=False, help="")
    space_args.add_argument("--sdk", default="gradio", nargs=1, choices=["gradio", "streamlit"])
    space_args.add_argument("--template", default="streamlit", help="A directory containing a project template directory, or a URL to a git repository.")
    space_args.add_argument("--organization", required=False, help="Organization to deploy new space under.")
    space_args.add_argument("--description", help="Description of new space")

    data_args = parser.add_argument_group("Data arguments")
    data_args.add_argument("--columns-to-index", nargs="+", default="content", help="Column to index in dataset")
    data_args.add_argument("--split", type=bool, required=False, default="train", help="Mode to open output file. Some modes overwrite existing file")
    data_args.add_argument("--dataset", type=bool, required=False, help="Local dataset folder or Huggingface name")
    data_args.add_argument("--docid-column", default="id", help="Name of docid column in dataset")
    data_args.add_argument("--language", default="en", help="ISO Code for language of dataset")

    index_args = parser.add_argument_group("Index arguments")
    index_args.add_argument("--collection", type=str, help="Collection class")
    index_args.add_argument("--memory_buffer", type=str, help="Memory buffer size")
    index_args.add_argument("--threads", type=int, default=5, help="Number of threads to use for indexing")
    index_args.add_argument("--use_hf_tokenizer", type=bool, default=False, help="If True, use HuggingFace tokenizer to tokenize dataset")
    index_args.add_argument("--pretokenized", type=bool, default=False, help="If True, dataset is already tokenized")
    index_args.add_argument("--store-positions", default=False, help="If True, store document vectors in index")
    index_args.add_argument("--store-docvectors", default=False, help="If True, store document vectors in index")
    index_args.add_argument("--store-contents", default=False, help="If True, store contents of documents in index")
    index_args.add_argument("--store-raw", default=False, help="If True, store raw contents of documents in index")
    index_args.add_argument("--keep-stopwords", type=bool, default=False, help="If True, keep stopwords in index")
    index_args.add_argument("--optimize-index", type=bool, help="If True, optimize index after indexing is complete")
    index_args.add_argument("--stopwords", type=str, help="Path to stopwords file")
    index_args.add_argument("--stemmer", type=str, nargs=1, choices=["porter", "krovetz"], help="Stemmer to use for indexing")
    
    args, _ = parser.parse_known_args()
    if args.config_file:
        config = json.load(open(args.config_file, "r"))
        args_dict = vars(args)
        args_dict.update(config)
    
    return args


def main():
    args = get_args()
    cookiecutter_vars = {
        "dset_text_field": args.columns_to_index, 
        "space_title": args.space_title, 
        "local_app": args.space_name,
        "space_description": args.description, 
        "dataset_name": args.dataset
    }

    local_app_dir = Path(f"apps/{args.space_name}")

    if args.command in ["index", "create", "deploy"]:
        logging.info(f"Indexing {args.dataset} dataset into {str(local_app_dir)}")
        index_streaming_dataset(
            dataset_name_or_path=args.dataset,
            index_path=str(local_app_dir / "index"),
            split=args.split,
            column_to_index=args.columns_to_index,
            doc_id_column=args.docid_column,
            language=args.language,
            storeContents=args.store_contents,
            storeRaw=args.store_raw
        )
    
    if args.command in ["create", "deploy"]:
        logging.info(f"Creating local app into {args.space_name} directory")
        create_app(template=args.template, extra_context_dict=cookiecutter_vars, output_dir="apps")

    if args.command == "deploy":
        logging.info(f"Creating space {args.space_name} on {args.organization}")
        create_space_from_local(
            space_slug=args.space_url_slug,
            organization=args.organization,
            space_sdk=args.sdk,
            local_dir=local_app_dir,
            delete_after_push=args.delete_after
        )


if __name__ == "__main__":
    main()
