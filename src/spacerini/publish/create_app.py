import os
import yaml
import shutil, errno

DEFAULT_APP_DIRECTORY="apps"
TEMPLATE_DIRECTORY="templates"

class StreamlitAppBuilder:
    def __init__(self, config_file: str) -> None:

        assert(os.path.exists(config_file) == True), "yaml file does not exist"
        self.config = yaml.safe_load(open(config_file))
        self._validate_config()
        self.app_directory = self._create_app_directory()

    def _create_app_directory(self) -> str:
        """

        :return:
        """
        app_directory=os.path.join(DEFAULT_APP_DIRECTORY, self.config["title"])
        os.makedirs(app_directory, exist_ok = True)
        assert (os.path.exists(app_directory)), f"Directory: {app_directory} was not created successfully"

        return app_directory

    def _write_packages_and_requirements(self):
        """

        :return:
        """
        packages_file_path=os.path.join(self.app_directory, "packages.txt")
        with open(packages_file_path, mode="w") as f:
            for package in self.config["packages"]:
                f.writelines(package+"\n")

        requirements_file_path=os.path.join(self.app_directory, "requirements.txt")
        with open(requirements_file_path, mode="w") as f:
            for dependency in self.config["dependencies"]:
                f.writelines(dependency+"\n")

        assert (os.path.exists(packages_file_path)), f"Packages file {packages_file_path} was not created successfully"
        assert (os.path.exists(requirements_file_path)), f"Requirements file {requirements_file_path} was not created successfully"


    def build_app(self):
        """

        :return:
        """
        self._write_packages_and_requirements()

        app_temp_file = os.path.join(TEMPLATE_DIRECTORY, f"{self.config['space_sdk']}/app_.txt")

        with open(app_temp_file) as temp_f, open(os.path.join(self.app_directory, "app.py"), mode="w") as f:
            content = temp_f.read()
            content = content.replace("{{title}}", self.config['title'])
            content = content.replace("{{page_icon}}", self.config['page_icon'])
            f.write(content)

        print(os.path.join(self.app_directory, "indices"))
        print(self.config['indices'])
        self._copy_indices(self.config['indices'], os.path.join(self.app_directory, "indices"))


    def _validate_config(self):
        pass

    def _copy_indices(self, source: str, dst: str):
        try:
            shutil.copytree(source, dst)
        except OSError as exc:
            if exc.errno in (errno.ENOTDIR, errno.EINVAL):
                shutil.copy(src, dst)
            else: raise


if __name__ == "__main__":
    builder = StreamlitAppBuilder(config_file="config/sample_config.yml")
    builder.build_app()





