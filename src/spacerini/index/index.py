def index_json_collection(shards_path, index_path, keep_shards):
# !python -m pyserini.index.lucene \
#   --collection JsonCollection \
#   --input to_index_json/ \
#   --index indexes/default_analyzer \
#   --generator DefaultLuceneDocumentGenerator \
#   --threads 20 \
#   --storePositions --storeDocvectors
    pass

def index_dataframe(df):
    pass

def index_streaming():
    pass

