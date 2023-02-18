# List of Parameters

## Indexing (`spacerini.index`)

-   `disable_tqdm` : bool 
        Disable tqdm output
-   `index_path` : str 
        Directory to store index
-   `language` : str
        Language of dataset
-   `pretokenized` : bool
        If True, dataset is already tokenized
-   `analyzeWithHuggingFaceTokenizer` : str
        If True, use HuggingFace tokenizer to tokenize dataset
-   `storePositions` : bool
        If True, store positions of tokens in index
-   `storeDocvectors` : bool
        If True, store document vectors in index
-   `storeContents` : bool
        If True, store contents of documents in index
-   `storeRaw` : bool
        If True, store raw contents of documents in index
-   `keepStopwords` : bool
        If True, keep stopwords in index
-   `stopwords` : str
        Path to stopwords file
-   `stemmer` : str
        Stemmer to use for indexing
-   `optimize` : bool
        If True, optimize index after indexing is complete
-   `verbose` : bool
        If True, print verbose output
-   `quiet` : bool
        If True, print no output
-   `memory_buffer` : str
        Memory buffer size
-   `n_threads` : bool
        Number of threads to use for indexing