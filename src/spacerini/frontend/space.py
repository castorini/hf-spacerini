from huggingface_hub import HfApi, create_repo, upload_folder
import shutil

def create_space_from_local(
    space_slug,
    space_sdk,
    local_dir,
    private=False,
    organization=None,
    delete_after_push=False,
    ):

    if organization is None:
        hf_api = HfApi()
        namespace = hf_api.whoami()["name"]
    else:
        namespace = organization
    repo_id =  namespace + "/" + space_slug
    repo_url = create_repo(repo_id=repo_id, repo_type="space", space_sdk=space_sdk, private=private)
    upload_folder(folder_path=local_dir, repo_id=repo_id, repo_type="space")
    if delete_after_push:
        shutil.rmtree(local_dir)
    return repo_url