import os
import yaml
import requests
from typing import List

from huggingface_hub import (
    create_repo,
    get_full_repo_name,
    upload_file,
    upload_folder
)


class SpaceBuilder:
    """
    Adapted from https://huggingface.co/spaces/farukozderim/Model-Comparator-Space-Builder
    """
    def __init__(self, config_file: str) -> None:
        assert(os.path.exists(config_file) == True), "yaml file does not exist"
        self.config = yaml.safe_load(open(config_file))
        self.error_message =  None
        self.url = None


    def check_space_name_availability(self, hf_token: str) -> bool:
        """
        Check whether if the space_name is currently used by the user or organization with the huggingface token.
        :param hf_token: hugging_face token
        :return: True if the space_name is available
        """
        try:
            repo_name = get_full_repo_name(model_id=self.config['space_name'], token=hf_token)
        except Exception as ex:
            print(ex)
            self.error_message = "You have given an incorrect HuggingFace token"
            return False

        try:
            url = f"https://huggingface.co/spaces/{repo_name}"
            response = requests.get(url)
            if response.status_code == 200:
                self.error_message = f"The {repo_name} is already used."
                return False
            else:
                print(f"The space name {repo_name} is available")
                return True
        except Exception as ex:
            print(ex)
            self.error_message = "Can not send a request to https://huggingface.co"
            return False


    def create_space(self, hf_token: str, local_app_folder:str=None,  repo_type: str="space") -> bool:
        """
        Creates the target space with the space name in the config file.
        :param hf_token: HuggingFace Write Token
        :param local_app_folder:
        :param repo_type:
        :return: True if success
        """
        try:
            create_repo(name=self.config['space_name'], token=hf_token, repo_type=repo_type, space_sdk=self.config['space_sdk'])
        except Exception as ex:
            print(ex)
            self.error_message = "Please provide a correct space name as Only regular characters and '-', '_', '.' accepted. '--' and '..' are forbidden. '-' and '.' cannot start or end the name."
            return False
        repo_name = get_full_repo_name(model_id=self.config['space_name'], token=hf_token)

        """
        use `upload folder` to upload directories
        """
        try:
            _ = upload_folder(
                folder_path=f"{local_app_folder}/indices",
                path_in_repo="indices",
                repo_id=repo_name,
                repo_type=repo_type,
                token=hf_token,
            )
            for file in ["packages.txt", "requirements.txt", "app.py"]:
                _ = upload_file(
                    path_or_fileobj=f"{local_app_folder}/{file}",
                    path_in_repo=file,
                    repo_id=repo_name,
                    repo_type=repo_type,
                    token=hf_token,
                )

            self.url = f"https://huggingface.co/spaces/{repo_name}"
            return True
        except Exception as ex:
            print(ex)
            self.error_message = (
                "An exception occurred during writing app.py to the target space"
            )
            return False


    def build_space(self, hf_token: str, local_app_folder: str) -> str:
        """
        Creates a space with given input spaces.
        :param model_or_space_names: Multiple model or space names split with new lines
        :param hf_token: HuggingFace token
        :param target_space_name: Target Space Name
        :param interface_title: Target Interface Title
        :param interface_description: Target Interface Description
        :return:
        """
        space_name=self.config['space_name']
        if (
                space_name== "" or space_name.isspace() or space_name is None
        ):
            return "Please fill all the inputs"
        if hf_token == "" or hf_token.isspace():
            hf_token = os.getenv('HF_TOKEN')

        if not self.check_space_name_availability(hf_token=hf_token):
            return self.error_message

        if not self.create_space(hf_token=hf_token, local_app_folder=local_app_folder):
            return self.error_message

        url = self.url
        return f"<a href={url}>{url}</a>"




if __name__ == "__main__":
    hf_token = os.getenv('HF_TOKEN')
    builder = SpaceBuilder(config_file="config/sample_config.yml")
    output = builder.build_space(hf_token=hf_token, local_app_folder="apps/Pyserini")
    print(output)