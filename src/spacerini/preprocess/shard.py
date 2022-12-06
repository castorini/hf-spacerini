from datasets import load_dataset


def load(path, ):
    pass

def shard():
    shards = [ds.shard(N_PARTITIONS, i, contiguous=True) for i in range(N_PARTITIONS)]
    pass

def save():
    pass