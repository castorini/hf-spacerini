from cookiecutter.main import cookiecutter

def create_app(
    template: str,
    extra_context_dict: dict,
    output_dir: str,
    no_input: bool=True,
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
        "https://github.com/cakiki/hf-spacerini",
        directory="templates/" + template,
        no_input=no_input,
        extra_context=extra_context_dict,
        output_dir=output_dir,
        overwrite_if_exists=overwrite_if_exists,
    )