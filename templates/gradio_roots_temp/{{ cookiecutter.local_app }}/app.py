from typing import List, NewType, Optional, Union

import gradio as gr

from spacerini_utils.index import fetch_index_stats
from spacerini_utils.search import _search, init_searcher, SearchResult

HTML = NewType('HTML', str)

searcher = init_searcher(sparse_index_path="sparse_index")

def get_docid_html(docid: Union[int, str]) -> HTML:
    {% if cookiecutter.private -%}
    docid_html = (
        f"<a "
        f'class="underline-on-hover"'
        f'style="color:#AA4A44;"'
        'href="https://huggingface.co/datasets/{{ cookiecutter.dataset_name }}"'
        'target="_blank"><b>🔒{{ cookiecutter.dataset_name }}</b></a><span style="color: #7978FF;">/'+f'{docid}</span>'
    )
    {%- else -%}
    docid_html = (
            f"<a "
            f'class="underline-on-hover"'
            'title="This dataset is licensed {{ cookiecutter.space_license }}"'
            f'style="color:#2D31FA;"'
            'href="https://huggingface.co/datasets/{{ cookiecutter.emoji }}"'
            'target="_blank"><b>🔒{{ cookiecutter.dataset_name }}</b></a><span style="color: #7978FF;">/'+f'{docid}</span>'
        ) 
    {%- endif %}

    return docid_html


def process_results(results: List[SearchResult], language: str, highlight_terms: Optional[List[str]] = None) -> HTML:
    if len(results) == 0:
        return """<br><p style='font-family: Arial; color:Silver; text-align: center;'>
                No results retrieved.</p><br><hr>"""

    results_html = ""
    for result in results:
        tokens = result["text"].split()

        tokens_html = []
        if highlight_terms:
            for token in tokens:
                if token in highlight_terms:
                    tokens_html.append("<b>{}</b>".format(token))
                else:
                    tokens_html.append(token)

        tokens_html = " ".join(tokens_html)
        meta_html = (
            """
                <p class='underline-on-hover' style='font-size:12px; font-family: Arial; color:#585858; text-align: left;'>
            """
        )
        docid_html = get_docid_html(result["docid"])
        results_html += """{}
            <p style='font-size:20px; font-family: Arial; color:#7978FF; text-align: left;'>Document ID: {}</p>
            <p style='font-size:14px; font-family: Arial; color:#7978FF; text-align: left;'>Score: {}</p>
            <p style='font-size:12px; font-family: Arial; color:MediumAquaMarine'>Language: {}</p>
            <p style='font-family: Arial;font-size:15px;'>{}</p>
            <br>
        """.format(
            meta_html, docid_html, result["score"], language, tokens_html
        )
    return results_html + "<hr>"


def search(query: str, language: str, num_results: int = 10) -> HTML:
    results_dict = _search(searcher, query, num_results=num_results)
    return process_results(results_dict, language)


stats = fetch_index_stats('sparse_index/')

description = f"""# <h2 style="text-align: center;"> {{ cookiecutter.emoji }} 🔎 {{ cookiecutter.space_title }} 🔍 {{ cookiecutter.emoji }} </h2>
<p style="text-align: center;font-size:15px;">{{ cookiecutter.space_description}}</p>
<p style="text-align: center;font-size:20px;">Dataset Statistics: Total Number of Documents = <b>{stats["documents"]}</b>, Number of Terms = <b>{stats["total_terms"]}</b> </p>"""

demo = gr.Blocks(
    css=".underline-on-hover:hover { text-decoration: underline; } .flagging { font-size:12px; color:Silver; }"
)

with demo:
    with gr.Row():
        gr.Markdown(value=description)
    with gr.Row():
        query = gr.Textbox(lines=1, max_lines=1, placeholder="Type your query here...", label="Query")
    with gr.Row():
        lang = gr.Dropdown(
            choices=[
                "en",
                "detect_language",
                "all",
            ],
            value="en",
            label="Language",
        )
    with gr.Row():
            k = gr.Slider(1, 100, value=10, step=1, label="Max Results")
    with gr.Row():
        submit_btn = gr.Button("Submit")
    with gr.Row():
        results = gr.HTML(label="Results")


    def submit(query: str, lang: str, k: int):
        query = query.strip()
        if query is None or query == "":
            return "", ""
        return {
            results: search(query, lang, k),
        }

    query.submit(fn=submit, inputs=[query, lang, k], outputs=[results])
    submit_btn.click(submit, inputs=[query, lang, k], outputs=[results])

demo.launch(enable_queue=True, debug=True)
