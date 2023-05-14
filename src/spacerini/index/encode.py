from pathlib import Path
from typing import List
from typing import Literal
from typing import Optional
from typing import Protocol

from pyserini.encode.__main__ import init_encoder
from pyserini.encode import RepresentationWriter
from pyserini.encode import FaissRepresentationWriter
from pyserini.encode import JsonlCollectionIterator
from pyserini.encode import JsonlRepresentationWriter

from spacerini.preprocess.utils import shard_dataset

EncoderClass = Literal["dkrr", "dpr", "tct_colbert", "ance", "sentence", "contriever", "auto"]


class Encoder(Protocol):
    def encode(**kwargs): ...


def init_writer(
    embedding_dir: str, 
    embedding_dimension: int = 768, 
    output_to_faiss: bool = False
) -> RepresentationWriter:
    if output_to_faiss:
        writer = FaissRepresentationWriter(embedding_dir, dimension=embedding_dimension)
        return writer

    return JsonlRepresentationWriter(embedding_dir)


def encode_corpus(
    corpus: str,
    encoder: Encoder,
    embedding_writer: RepresentationWriter, 
    batch_size: int, 
    shard_id: int,
    shard_num: int,
    delimiter: str = "\n",
    max_length: int = 256,
    add_sep: bool = False,
    input_fields: List[str] = ["text"],
    fields_to_encode: Optional[List[str]] = None,
    fp16: bool = False
) -> None:
    if input_fields is None:
        input_fields = ["text"]
    
    if fields_to_encode is None:
        fields_to_encode = ["text"]
    
    collection_iterator = JsonlCollectionIterator(corpus, input_fields, delimiter)

    with embedding_writer:
        for batch_info in collection_iterator(batch_size, shard_id, shard_num):
            kwargs = {
                'texts': batch_info['text'],
                'titles': batch_info['title'] if 'title' in fields_to_encode else None,
                'expands': batch_info['expand'] if 'expand' in fields_to_encode else None,
                'fp16': fp16,
                'max_length': max_length,
                'add_sep': add_sep,
            }
            embeddings = encoder.encode(**kwargs)
            batch_info['vector'] = embeddings
            embedding_writer.write(batch_info, input_fields)


def encode_json_shards(
    shards_path: str,
    encoder_name_or_path: str,
    encoder_class: EncoderClass,
    embedding_dir: str,
    batch_size: int,
    device: str = "cuda:0",
    num_shards: int = 1,
    delimiter: str = "\n",
    max_length: int = 256,
    add_sep: bool = False,
    input_fields: List[str] = ["text"],
    fields_to_encode: Optional[List[str]] = None,
    output_to_faiss: bool = False,
    embedding_dimension: int = 768,
    fp16: bool = False
) -> None:
    encoder = init_encoder(encoder_name_or_path, encoder_class, device=device)

    # input_dir = Path(shards_path)
    # output_dir = Path(embedding_dir)
    
    writer = init_writer(
        embedding_dir=embedding_dir, 
        embedding_dimension=embedding_dimension, 
        output_to_faiss=output_to_faiss
    )

        # encode_corpus(
        #     corpus=shards_path,
        #     encoder=encoder,
        #     embedding_writer=writer,
        #     batch_size=batch_size,
        #     delimiter=delimiter,
        #     input_fields=input_fields,

        # )

