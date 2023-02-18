from datasets import Dataset, IterableDataset
import pandas as pd
import ir_datasets
from typing import Generator, Dict

def ir_dataset_dict_generator(ds_name: str) -> Generator[Dict,None,None]:
    dataset = ir_datasets.load(ds_name)
    for doc in dataset.docs_iter():
        yield {
            "contents": doc.text,
            "docid": doc.doc_id
            }

def load_ir_dataset(ds_name: str) -> Dataset:
    dataset = ir_datasets.load(ds_name)
    return Dataset.from_pandas(pd.DataFrame(dataset.docs_iter()))

def load_ir_dataset_streaming(ds_name: str) -> IterableDataset:
    return IterableDataset.from_generator(ir_dataset_dict_generator, gen_kwargs={"ds_name": ds_name})

def load_from_pandas(df: pd.DataFrame) -> Dataset:
    return Dataset.from_pandas(df)

def load_from_sqlite_table(uri_or_con: str, table_or_query: str) -> Dataset:
    return Dataset.from_sql(con=uri_or_con, sql=table_or_query)
