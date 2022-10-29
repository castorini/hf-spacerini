import os
import yaml

DEFAULT_APP_DIRECTORY="apps"

class StreamlitAppBuilder():
    def __init__(self, config_file: str) -> None:

        assert(os.path.exists(config_file) == True), "yaml file does not exist"
        self.config = yaml.load(config_file)

    def _create_app_directory(self):

        app_directory = self.config["app_local_path"] if  os.path.exists(self.config["app_local_path"]) else DEFAULT_APP_DIRECTORY
        os.makedirs(os.path.join(app_directory, self.config["title"]))



