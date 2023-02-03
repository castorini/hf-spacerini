import os
import argparse
import logging
from spacerini.frontend import create_space_from_local, create_app

logger = logging.getLogger(__name__)


def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--template",
        type=str,
        help="The path to a predefined template to use.",
        required=True
    )
    parser.add_argument(
        "--extra_context_dict",
        type=dict,
        help="The extra context to pass to the template.",
    )
    parser.add_argument(
        "--no_input",
        type=bool,
        help="If True, do not prompt for parameters and only use",
    )
    parser.add_argument(
        "--overwrite_if_exists",
        type=bool,
        help="If True, overwrite the output directory if it already exists.",
        default=True
    )
    parser.add_argument(
        "--space_slug",
        type=str,
        help="The name of the space on huggingface.",
        required=True
    )
    parser.add_argument(
        "--space_sdk",
        type=str,
        help="The SDK of the space, could be either Gradio or Streamlit.",
        choices=["gradio", "streamlit"],
        required=True
    )
    parser.add_argument(
        "--local_dir",
        type=str,
        help="The local directory where the app should be stored.",
    )
    parser.add_argument(
        "--private",
        type=bool,
        help="If True, the space will be private.",
        default=False
    )
    parser.add_argument(
        "--organization",
        type=str,
        help="The organization to create the space in.",
        default=None
    )
    parser.add_argument(
        "--delete_after_push",
        type=bool,
        help="If True, delete the local directory after pushing it to the Hub.",
    )
    return parser

def main():
    parser = parser()
    args = parser.parse_args()

    logger.info("Validating the input arguments...")
    assert os.path.exists(args.template), "The template does not exist."
    assert os.path.exists(args.local_dir), "The local directory does not exist."

    logger.info("Creating the app locally...")
    create_app(
        template=args.template,
        extra_context_dict=args.extra_context_dict,
        output_dir=args.local_dir,
        no_input=args.no_input,
        overwrite_if_exists=args.overwrite_if_exists
    )

    logger.info("Creating the space on huggingface...")
    create_space_from_local(
        space_slug=args.space_slug,
        space_sdk=args.space_sdk,
        local_dir=args.local_dir,
        private=args.private,
        organization=args.organization,
        delete_after_push=args.delete_after_push
    )


if __name__ == "__main__":
    pass