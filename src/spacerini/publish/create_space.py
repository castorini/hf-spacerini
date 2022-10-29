from typing import List

import requests
import gradio as gr
import os


from huggingface_hub import (
    create_repo,
    get_full_repo_name,
    upload_file,
)


class SpaceBuilder:
    """
    Adapted from https://huggingface.co/spaces/farukozderim/Model-Comparator-Space-Builder
    """
    error_message =  None
    url = None

    @classmethod
    def split_space_names(cls, names: str) -> List[str]:
        """
        Splits and filters the given space_names.
        :param names: space names
        :return: Name List
        """
        name_list = names.split("\n")
        filtered_list = []
        for name in name_list:
            if not (name == "" or name.isspace()):
                name = name.replace(" ", "")
                filtered_list.append(name)
        return filtered_list

    @classmethod
    def check_space_name_availability(cls, hf_token: str, space_name: str) -> bool:
        """
        Check whether if the space_name is currently used.
        :param hf_token: hugging_face token
        :param space_name:
        :return: True if the space_name is available
        """
        try:
            repo_name = get_full_repo_name(model_id=space_name, token=hf_token)
        except Exception as ex:
            print(ex)
            cls.error_message = "You have given an incorrect HuggingFace token"
            return False
        try:
            url = f"https://huggingface.co/spaces/{repo_name}"
            response = requests.get(url)
            if response.status_code == 200:
                cls.error_message = f"The {repo_name} is already used."
                return False
            else:
                print(f"The space name {repo_name} is available")
                return True
        except Exception as ex:
            print(ex)
            cls.error_message = "Can not send a request to https://huggingface.co"
            return False


    @classmethod
    def create_space(cls, input_space_names: str, target_space_name: str, hf_token: str, title: str, description: str, space_sdk: str, repo_type: str="space"  ) -> bool:
        """
        Creates the target space with the given space names.
        :param input_space_names: Input space name_list
        :param target_space_name: Target space_name
        :param hf_token: HuggingFace Write Token
        :param title: Target Interface Title
        :param description: Target Interface Description
        :return: True if success
        """
        name_list = cls.split_space_names(input_space_names)
        try:
            create_repo(name=target_space_name, token=hf_token, repo_type=repo_type, space_sdk=space_sdk)
        except Exception as ex:
            print(ex)
            cls.error_message = "Please provide a correct space name as Only regular characters and '-', '_', '.' accepted. '--' and '..' are forbidden. '-' and '.' cannot start or end the name."
            return False
        repo_name = get_full_repo_name(model_id=target_space_name, token=hf_token)

        try:
            file_string = cls.file_as_a_string(name_list, title, description)
            temp_file = open("temp_file.txt", "w")
            temp_file.write(file_string)
            temp_file.close()
        except Exception as ex:
            print(ex)
            cls.error_message = "An exception occurred during temporary file writing"
            return False

        """
        use `upload folder` to upload directories
        """
        try:
            file_url = upload_file(
                path_or_fileobj="temp_file.txt",
                path_in_repo="app.py",
                repo_id=repo_name,
                repo_type=repo_type,
                token=hf_token,
            )
            cls.url = f"https://huggingface.co/spaces/{repo_name}"
            return True
        except Exception as ex:
            print(ex)
            cls.error_message = (
                "An exception occurred during writing app.py to the target space"
            )
            return False

    @staticmethod
    def build_space(
            model_or_space_names: str, hf_token: str, target_space_name: str, interface_title: str, interface_description: str
    ) -> str:
        """
        Creates a space with given input spaces.
        :param model_or_space_names: Multiple model or space names split with new lines
        :param hf_token: HuggingFace token
        :param target_space_name: Target Space Name
        :param interface_title: Target Interface Title
        :param interface_description: Target Interface Description
        :return:
        """
        if (
                model_or_space_names== "" or model_or_space_names.isspace()
                or target_space_name == "" or target_space_name.isspace()
                or interface_title == "" or interface_title.isspace()
                or interface_description == "" or interface_description.isspace()
        ):
            return "Please fill all the inputs"
        if hf_token == "" or hf_token.isspace():
            hf_token = os.environ['HF_SELF_TOKEN']
        if not SpaceBuilder.check_space_name_availability(hf_token=hf_token, space_name=target_space_name):
            return SpaceBuilder.error_message
        if not SpaceBuilder.load_and_check_spaces(names=model_or_space_names):
            return SpaceBuilder.error_message
        if not SpaceBuilder.create_space(input_space_names=model_or_space_names, target_space_name=target_space_name, hf_token=hf_token, title=interface_title, description=interface_description):
            return SpaceBuilder.error_message

        url = SpaceBuilder.url
        return f"<a href={url}>{url}</a>"