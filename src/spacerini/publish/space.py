from huggingface_hub import HfApi, Repository, create_repo

def create_space(space_slug, local_dir, space_sdk, private=False, organization=None):
    if organization is None:
        hf_api = HfApi()
        namespace = hf_api.whoami()["name"]
    else:
        namespace = organization
    repo_url = create_repo(namespace + "/" + space_slug, repo_type="space", space_sdk=space_sdk, private=private)
    repository = Repository(local_dir=local_dir, clone_from=repo_url)
    repository.git_add()
    repository.git_commit("Create Space")
    repository.git_push()