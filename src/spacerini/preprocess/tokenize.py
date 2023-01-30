def batch_iterator(hf_dataset, text_field, batch_size=1000):
    for i in range(0, len(hf_dataset), batch_size):
        yield hf_dataset.select(range(i, i + batch_size))[text_field]