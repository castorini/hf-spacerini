import argparse
import json
import logging
from pathlib import Path
from shutil import copytree

from spacerini.frontend import create_app, create_space_from_local
from spacerini.index import index_streaming_dataset
from spacerini.index.encode import encode_json_dataset
from spacerini.prebuilt import EXAMPLES


def update_args_from_json(_args: argparse.Namespace, file: str) -> argparse.Namespace:
    config = json.load(open(file, "r"))
    config = {k.replace("-", "_"): v for k,v in config.items()}
    
    args_dict = vars(_args)
    args_dict.update(config)
    return _args


# TODO: @theyorubayesian: Switch to HFArgumentParser with post init
# How to use multiple argparse commands with HFArgumentParser
def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="Spacerini",
        description="A modular framework for seamless building and deployment of interactive search applications.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="Written by: Akintunde 'theyorubayesian' Oladipo <akin.o.oladipo@gmail.com>, Christopher Akiki <christopher.akiki@gmail.com>, Odunayo Ogundepo <ogundepoodunayo@gmail.com>"
    )
    parser.add_argument("--space-name", required=False)
    parser.add_argument("--config-file", type=str, help="Path to configuration for space")
    parser.add_argument("--from-example", type=str, choices=list(EXAMPLES), help="Name of an example spaces applications.")
    parser.add_argument("--verbose", type=bool, default=True, help="If True, print verbose output")
    parser.add_argument("--index-exists", type=str, help="Path to an existing index to be used for Spaces application")

    # --------
    # Commands
    # --------
    sub_parser = parser.add_subparsers(dest="command", title="Commands", description="Valid commands")
    index_parser = sub_parser.add_parser("index", help="Index dataset. This will not create the app or deploy it.")
    create_parser = sub_parser.add_parser("create-space", help="Create space in local directory. This won't deploy the space.")
    deploy_only_parser = sub_parser.add_parser("deploy-only", help="Deploy an already created space")
    deploy_parser = sub_parser.add_parser("deploy", help="Deploy new space.")
    deploy_parser.add_argument("--delete-after", type=bool, default=False, help="If True, delete the local directory after pushing it to the Hub.")
    # --------

    space_args = parser.add_argument_group("Space arguments")
    space_args.add_argument("--space-title", required=False, help="Title to show on Space")
    space_args.add_argument("--space-url-slug", required=False, help="")
    space_args.add_argument("--sdk", default="gradio", choices=["gradio", "streamlit"])
    space_args.add_argument("--template", default="streamlit", help="A directory containing a project template directory, or a URL to a git repository.")
    space_args.add_argument("--organization", required=False, help="Organization to deploy new space under.")
    space_args.add_argument("--description", type=str, help="Description of new space")
    space_args.add_argument("--private", action="store_true", help="Deploy private Spaces application")

    data_args = parser.add_argument_group("Data arguments")
    data_args.add_argument("--columns-to-index", default=[], action="store", nargs="*", help="Other columns to index in dataset")
    data_args.add_argument("--split", type=str, required=False, default="train", help="Dataset split to index")
    data_args.add_argument("--dataset", type=str, required=False, help="Local dataset folder or Huggingface name")
    data_args.add_argument("--docid-column", default="id", help="Name of docid column in dataset")
    data_args.add_argument("--language", default="en", help="ISO Code for language of dataset")
    data_args.add_argument("--title-column", type=str, help="Name of title column in data")
    data_args.add_argument("--content-column", type=str, default="content", help="Name of content column in data")
    data_args.add_argument("--expand-column", type=str, help="Name of column containing document expansion. Used in dense indexes")

    sparse_index_args = parser.add_argument_group("Sparse Index arguments")
    sparse_index_args.add_argument("--collection", type=str, help="Collection class")
    sparse_index_args.add_argument("--memory-buffer", type=str, help="Memory buffer size")
    sparse_index_args.add_argument("--threads", type=int, default=5, help="Number of threads to use for indexing")
    sparse_index_args.add_argument("--hf-tokenizer", type=str, default=None, help="HuggingFace tokenizer to tokenize dataset")
    sparse_index_args.add_argument("--pretokenized", type=bool, default=False, help="If True, dataset is already tokenized")
    sparse_index_args.add_argument("--store-positions", action="store_true", help="If True, store document vectors in index")     # TODO: @theyorubayesian
    sparse_index_args.add_argument("--store-docvectors", action="store_true", help="If True, store document vectors in index")    # TODO: @theyorubayesian
    sparse_index_args.add_argument("--store-contents", action="store_true", help="If True, store contents of documents in index")
    sparse_index_args.add_argument("--store-raw", action="store_true", help="If True, store raw contents of documents in index")
    sparse_index_args.add_argument("--keep-stopwords", action="store_true", help="If True, keep stopwords in index")
    sparse_index_args.add_argument("--optimize-index", action="store_true", help="If True, optimize index after indexing is complete")
    sparse_index_args.add_argument("--stopwords", type=str, help="Path to stopwords file")
    sparse_index_args.add_argument("--stemmer", type=str, nargs=1, choices=["porter", "krovetz"], help="Stemmer to use for indexing")
    
    dense_index_args = parser.add_argument_group("Dense Index arguments")
    dense_index_args.add_argument("--encoder-name-or-path", type=str, help="Encoder name or path")
    dense_index_args.add_argument("--encoder-class", default="auto", type=str, choices=["dpr", "bpr", "tct_colbert", "ance", "sentence-transformers", "auto"], help="Encoder to use")
    dense_index_args.add_argument("--delimiter", default="\n", type=str, help="Delimiter for the fields in encoded corpus")
    dense_index_args.add_argument("--index-shard-id", default=0, type=int, help="Zero-based index shard id")
    dense_index_args.add_argument("--n-index-shards", type=int, default=1, help="Number of index shards")
    dense_index_args.add_argument("--batch-size", default=64, type=int, help="Batch size for encoding")
    dense_index_args.add_argument("--max-length", type=int, default=256, help="Max document length to encode")
    dense_index_args.add_argument('--device', default='cuda:0', type=str, help='Device: cpu or cuda [cuda:0, cuda:1...]', required=False)
    dense_index_args.add_argument("--dimension", default=768, type=int, help="Dimension for Faiss Index")
    dense_index_args.add_argument("--add-sep", action="store_true", help="Pass `title` and `content` columns separately into encode function")
    dense_index_args.add_argument("--to-faiss", action="store_true", help="Store embeddings in Faiss Index")
    dense_index_args.add_argument("--fp16", action="store_true", help="Use FP 16")

    search_args = parser.add_argument_group("Search arguments")
    search_args.add_argument("--bm25_k1", type=float, help="BM25: k1 parameter")
    search_args.add_argument("--bm24_b", type=float, help="BM25: b parameter")

    args, _ = parser.parse_known_args()

    if args.from_example in EXAMPLES:
        example_config_path = Path(__file__).parents[2] / "examples" \
            / "configs" / f"{args.from_example}.json"
        args = update_args_from_json(args, example_config_path)

    # For customization, user provided config file supersedes example config file
    if args.config_file:
        args = update_args_from_json(args, args.config_file)

    args.template = "templates/gradio_roots_temp"
    return args


def main():
    args = get_args()

    local_app_dir = Path(f"apps/{args.space_name}")
    local_app_dir.mkdir(exist_ok=True)

    columns = [args.content_column, *args.columns_to_index]

    if args.command in ["index", "create-space", "deploy"]:       
        logging.info(f"Indexing {args.dataset} dataset into {str(local_app_dir)}")

        if args.index_exists:
            index_dir = Path(args.index_exists)
            assert index_dir.exists(), f"No index found at {args.index_exists}"
            copytree(index_dir, local_app_dir / index_dir.name, dirs_exist_ok=True)
        else:
            # TODO: @theyorubayesian
            # We always create a sparse index because dense index only contain docid. Does this make sense memory-wise? 
            # Another option could be to load the dataset from huggingface and filter documents by docids retrieved
            # Can documents be stored in dense indexes? Does it make sense to?
            index_streaming_dataset(
                dataset_name_or_path=args.dataset,
                index_path=(local_app_dir / "sparse_index").as_posix(),
                split=args.split,
                column_to_index=columns,
                doc_id_column=args.docid_column,
                language=args.language,
                storeContents=args.store_contents,
                storeRaw=args.store_raw,
                analyzeWithHuggingFaceTokenizer=args.hf_tokenizer
            )

            if args.encoder_name_or_path:
                encode_json_dataset(
                    data_path=args.dataset,
                    encoder_name_or_path=args.encoder_name_or_path,
                    encoder_class=args.encoder_class,
                    embedding_dir=(local_app_dir / "dense_index").as_posix(),
                    batch_size=args.batch_size,
                    device=args.device,
                    index_shard_id=args.index_shard_id,
                    num_index_shards=args.n_index_shards,
                    delimiter=args.delimiter,
                    max_length=args.max_length,
                    add_sep=args.add_sep,
                    title_column_to_encode=args.title_column,
                    text_column_to_encode=args.content_column,
                    expand_column_to_encode=args.expand_column,
                    output_to_faiss=True,
                    embedding_dimension=args.dimension,
                    fp16=args.fp16
                )
    
    if args.command in ["create-space", "deploy"]:
        logging.info(f"Creating local app into {args.space_name} directory")
        # TODO: @theyorubayesian - How to make cookiecutter_vars more flexible
        cookiecutter_vars = {
            "dset_text_field": columns, 
            "space_title": args.space_title, 
            "local_app": args.space_name,
            "space_description": args.description, 
            "dataset_name": args.dataset
        }

        create_app(
            template=args.template, 
            extra_context_dict=cookiecutter_vars, 
            output_dir="apps"
        )

    if args.command in ["deploy", "deploy-only"]:
        logging.info(f"Creating space {args.space_name} on {args.organization}")
        create_space_from_local(
            space_slug=args.space_url_slug,
            organization=args.organization,
            space_sdk=args.sdk,
            local_dir=local_app_dir,
            delete_after_push=args.delete_after,
            private=args.private
        )


if __name__ == "__main__":
    main()
