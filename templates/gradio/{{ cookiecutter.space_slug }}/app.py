import gradio as gr
from datasets import load_dataset
# TODO after release: from spacerini import search, format_results

def search(query):
    results = 5 * query
    return results

def format_results(results):
    return results

# ds = load_dataset({{ cookiecutter.hf_dataset }})

if __name__ == "__main__":
    search_engine = gr.Blocks()

    with search_engine:
        with gr.Row():
            gr.Markdown(value="""# <p style="text-align: center;"> {{ cookiecutter.space_title }} </p>""")
        with gr.Row():
            query = gr.Textbox(lines=1, max_lines=1, placeholder="Search…", label="Query")
        with gr.Row():
            submit_btn = gr.Button("🔍")
        with gr.Row():
            results = gr.HTML(label="Results")
        query.submit(fn=search, inputs=[query], outputs=[results])
        submit_btn.click(search, inputs=[query], outputs=[results])

    search_engine.launch(enable_queue=True, debug=True)