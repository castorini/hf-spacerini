from huggingface_hub import HfApi, create_repo, upload_folder
import shutil
import logging

logger = logging.getLogger(__name__)

def create_space_from_local(
    space_slug: str,
    space_sdk: str,
    local_dir: str,
    private: bool=False,
    organization: str=None,
    delete_after_push: bool=False,
    ) -> str:
    """
    Create a new space from a local directory.
    Parameters
    ----------
    space_slug : str
        The slug of the space.
    space_sdk : str
        The SDK of the space, could be either Gradio or Streamlit.
    local_dir : str
        The local directory where the app is currently stored.
    private : bool, optional
        If True, the space will be private.
    organization : str, optional
        The organization to create the space in.
    delete_after_push : bool, optional
        If True, delete the local directory after pushing it to the Hub.
    
    Returns
    -------
    repo_url: str
        The URL of the space.
    """

    if organization is None:
        hf_api = HfApi()
        namespace = hf_api.whoami()["name"]
    else:
        namespace = organization
    repo_id =  namespace + "/" + space_slug
    try:
        repo_url = create_repo(repo_id=repo_id, repo_type="space", space_sdk=space_sdk, private=private)
    except Exception as ex:
        logger.error("Encountered an error while creating the space: ", ex)
        raise
        
    upload_folder(folder_path=local_dir, repo_id=repo_id, repo_type="space")
    if delete_after_push:
        shutil.rmtree(local_dir)
    return repo_url