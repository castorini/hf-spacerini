from pathlib import Path
from shutil import copytree

from cookiecutter.main import cookiecutter

default_templates_dir = (Path(__file__).parents[3] / "templates").resolve()
LOCAL_TEMPLATES = ["gradio", "streamlit", "gradio_roots_temp"]


def create_app(
    template: str,
    extra_context_dict: dict,
    output_dir: str,
    no_input: bool = True,
    overwrite_if_exists: bool=True
    ) -> None:
    """
    Create a new app from a template.
    Parameters
    ----------
    template : str
        The name of the template to use.
    extra_context_dict : dict
        The extra context to pass to the template.
    output_dir : str
        The output directory.
    no_input : bool, optional
        If True, do not prompt for parameters and only use
    overwrite_if_exists : bool, optional
        If True, overwrite the output directory if it already exists.
    Returns
    -------
    None
    """
    cookiecutter(
        "https://github.com/castorini/hf-spacerini.git/" if template in LOCAL_TEMPLATES else template,
        directory="templates/" + template if template in LOCAL_TEMPLATES else None,
        no_input=no_input,
        extra_context=extra_context_dict,
        output_dir=output_dir,
        overwrite_if_exists=overwrite_if_exists,
    )

    utils_dir = Path(__file__).parents[1].resolve() / "spacerini_utils"
    app_dir = Path(output_dir) / extra_context_dict["local_app"] / "spacerini_utils"
    copytree(utils_dir, app_dir, dirs_exist_ok=True)
    
    return None
