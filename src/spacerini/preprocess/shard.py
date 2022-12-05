from datasets import load_dataset

shards = [ds.shard(N_PARTITIONS, i, contiguous=True) for i in range(N_PARTITIONS)]
