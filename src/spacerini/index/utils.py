import shutil
import logging
from huggingface_hub import HfApi, create_repo, upload_folder, snapshot_download

logger = logging.getLogger(__name__)


def push_index_to_hub(
    dataset_slug: str,
    index_path: str,
    private: bool=False,
    organization: str=None,
    delete_after_push: bool=False,
    ) -> str:
    """
    Push an index as a dataset to the Hugging Face Hub.
    ----------
    dataset_slug : str
        The slug of the space.
    index_path : str
        The local directory where the app is currently stored.
    private : bool, optional
        If True, the space will be private.
    organization : str, optional
        The organization to create the space in.
    delete_after_push : bool, optional
        If True, delete the local index after pushing it to the Hub.
    
    Returns
    -------
    repo_url: str
        The URL of the dataset.
    """

    if organization is None:
        hf_api = HfApi()
        namespace = hf_api.whoami()["name"]
    else:
        namespace = organization
    repo_id =  namespace + "/" + dataset_slug
    try:
        repo_url = create_repo(repo_id=repo_id, repo_type="dataset", private=private)
    except Exception as ex:
        logger.error("Encountered an error while creating the dataset repository: ", ex)
        raise
        
    upload_folder(folder_path=index_path, path_in_repo="index", repo_id=repo_id, repo_type="dataset")
    if delete_after_push:
        shutil.rmtree(index_path)
    return repo_url

def load_index_from_hub(dataset_slug: str, organization: str=None) -> str:
    if organization is None:
        hf_api = HfApi()
        namespace = hf_api.whoami()["name"]
    else:
        namespace = organization
    repo_id =  namespace + "/" + dataset_slug
    
    local_path = snapshot_download(repo_id=repo_id, repo_type="dataset")
    index_path = local_path + "/index"
    return index_path


