from cookiecutter.main import cookiecutter

def create_app(
    template,
    extra_context_dict,
    output_dir,
    no_input=True,
    overwrite_if_exists=True
    ):
    cookiecutter(
        "https://github.com/cakiki/hf-spacerini",
        directory="templates/" + template,
        no_input=no_input,
        extra_context=extra_context_dict,
        output_dir=output_dir,
        overwrite_if_exists=overwrite_if_exists,
    )