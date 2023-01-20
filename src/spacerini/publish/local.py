from cookiecutter.main import cookiecutter

def create_app(template, extra_context_dict, output_dir):
    cookiecutter(
        "https://github.com/castorini/hf-spacerini",
        directory="templates/" + template,
        no_input=True,
        extra_context=extra_context_dict,
        output_dir=output_dir,
        overwrite_if_exists=True,
    )