from huggingface_hub import HfApi, Repository, create_repo
from .local import create_app

def create_space(
    space_slug,
    local_dir,
    space_sdk,
    template,
    private=False,
    organization=None,
    *args,
    **kwargs,
    ):

    if organization is None:
        hf_api = HfApi()
        namespace = hf_api.whoami()["name"]
    else:
        namespace = organization
    repo_url = create_repo(namespace + "/" + space_slug, repo_type="space", space_sdk=space_sdk, private=private)
    create_app(output_dir=local_dir, template=template, extra_context_dict=kwargs)
    repository = Repository(local_dir=local_dir)
    repository.git_add()
    repository.git_commit("add module default template")
    repository.git_push()
    return repo_url