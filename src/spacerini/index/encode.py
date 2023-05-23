from typing import Iterable
from typing import List
from typing import Literal
from typing import Optional
from typing import Protocol

from pyserini.encode.__main__ import init_encoder
from pyserini.encode import RepresentationWriter
from pyserini.encode import FaissRepresentationWriter
from pyserini.encode import JsonlCollectionIterator
from pyserini.encode import JsonlRepresentationWriter

EncoderClass = Literal["dkrr", "dpr", "tct_colbert", "ance", "sentence", "contriever", "auto"]


class Encoder(Protocol):
    def encode(**kwargs): ...


def init_writer(
    embedding_dir: str, 
    embedding_dimension: int = 768, 
    output_to_faiss: bool = False
) -> RepresentationWriter:
    """
    """
    if output_to_faiss:
        writer = FaissRepresentationWriter(embedding_dir, dimension=embedding_dimension)
        return writer

    return JsonlRepresentationWriter(embedding_dir)


def encode_corpus_or_shard(
    encoder: Encoder,
    collection_iterator: Iterable[dict],
    embedding_writer: RepresentationWriter, 
    batch_size: int, 
    shard_id: int,
    shard_num: int,
    max_length: int = 256,
    add_sep: bool = False,
    input_fields: List[str] = None,
    title_column_to_encode: Optional[str] = None,
    text_column_to_encode: Optional[str] = "text",
    expand_column_to_encode: Optional[str] = None,
    fp16: bool = False
) -> None:
    """
    
    """
    with embedding_writer:
        for batch_info in collection_iterator(batch_size, shard_id, shard_num):
            kwargs = {
                'texts': batch_info[text_column_to_encode],
                'titles': batch_info[title_column_to_encode] if title_column_to_encode else None,
                'expands': batch_info[expand_column_to_encode] if expand_column_to_encode else None,
                'fp16': fp16,
                'max_length': max_length,
                'add_sep': add_sep,
            }
            embeddings = encoder.encode(**kwargs)
            batch_info['vector'] = embeddings
            embedding_writer.write(batch_info, input_fields)


def encode_json_dataset(
    data_path: str,
    encoder_name_or_path: str,
    encoder_class: EncoderClass,
    embedding_dir: str,
    batch_size: int,
    index_shard_id: int = 0,
    num_index_shards: int = 1,
    device: str = "cuda:0",
    delimiter: str = "\n",
    max_length: int = 256,
    add_sep: bool = False,
    input_fields: List[str] = None,
    title_column_to_encode: Optional[str] = None,
    text_column_to_encode: Optional[str] = "text",
    expand_column_to_encode: Optional[str] = None,
    output_to_faiss: bool = False,
    embedding_dimension: int = 768,
    fp16: bool = False
) -> None:
    """
    
    """
    if input_fields is None:
        input_fields = ["text"]
    
    encoder = init_encoder(encoder_name_or_path, encoder_class, device=device)

    writer = init_writer(
        embedding_dir=embedding_dir, 
        embedding_dimension=embedding_dimension, 
        output_to_faiss=output_to_faiss
    )

    collection_iterator = JsonlCollectionIterator(data_path, input_fields, delimiter)
    encode_corpus_or_shard(
        encoder=encoder,
        collection_iterator=collection_iterator,
        embedding_writer=writer,
        batch_size=batch_size,
        shard_id=index_shard_id,
        shard_num=num_index_shards,
        max_length=max_length,
        add_sep=add_sep,
        input_fields=input_fields,
        title_column_to_encode=title_column_to_encode,
        text_column_to_encode=text_column_to_encode,
        expand_column_to_encode=expand_column_to_encode,
        fp16=fp16
    )
