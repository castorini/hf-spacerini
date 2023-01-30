import gradio as gr
from datasets import load_dataset
from pyserini.search.lucene import LuceneSearcher

searcher = LuceneSearcher("index")
ds = load_dataset( "{{ cookiecutter.hf_dataset }}", split="{{ cookiecutter.hf_dataset_split }}")

def search(query):
    hits = searcher.search(query, k=10)
    results = ds.select([int(hit.docid) for hit in hits])
    return results['text']


if __name__ == "__main__":
    demo = gr.Blocks()

    with demo:
        with gr.Row():
            gr.Markdown(value="""# <p style="text-align: center;"> {{ cookiecutter.space_title }} </p>""")
        with gr.Row():
            query = gr.Textbox(lines=1, max_lines=1, placeholder="Search…", label="Query")
        with gr.Row():
            submit_btn = gr.Button("🔍")
        with gr.Column():
            c1 = gr.HTML(label="Results")
            c2 = gr.HTML(label="Results")
            c3 = gr.HTML(label="Results")
            c4 = gr.HTML(label="Results")
            c5 = gr.HTML(label="Results")
            c6 = gr.HTML(label="Results")
            c7 = gr.HTML(label="Results")
            c8 = gr.HTML(label="Results")
            c9 = gr.HTML(label="Results")
            c10 = gr.HTML(label="Results")
        query.submit(fn=search, inputs=[query], outputs=[c1, c2, c3, c4, c5, c6, c7, c8, c9, c10])
        submit_btn.click(search, inputs=[query], outputs=[c1, c2, c3, c4, c5, c6, c7, c8, c9, c10])

    demo.launch(enable_queue=True, debug=True)