import http.client as http_client
import json
import logging
import os
import re
import string
import traceback

import gradio as gr
from typing import Callable, Optional, Tuple, Union
from pyserini import util
from pyserini.search import LuceneSearcher, FaissSearcher, AutoQueryEncoder


def _load_sparse_searcher(language: str, k1: Optional[float]=None, b: Optional[float]=None) -> (Searcher):
    searcher = LuceneSearcher(f'index/')
    searcher.set_language(language)
    if k1 is not None and b is not None:
        searcher.set_bm25(k1, b)
        retriever_name = f'BM25 (k1={k1}, b={b})'
    else:
        retriever_name = 'BM25'

    return searcher


def get_docid_html(docid):
    if {{ cookiecutter.private }}:
        docid_html = (
            f"<a "
            f'class="underline-on-hover"'
            f'style="color:#AA4A44;"'
            'href="https://huggingface.co/datasets/{{ cookiecutter.emoji }}"'
            'target="_blank"><b>🔒{{ cookiecutter.dataset_name }}</b></a><span style="color: #7978FF;">/'+f'{docid}</span>'
        )
    else:
        docid_html = (
            f"<a "
            f'class="underline-on-hover"'
            'title="This dataset is licensed {{ cookiecutter.space_license }}"'
            f'style="color:#2D31FA;"'
            'href="https://huggingface.co/datasets/{{ cookiecutter.emoji }}"'
            'target="_blank"><b>🔒{{ cookiecutter.dataset_name }}</b></a><span style="color: #7978FF;">/'+f'{docid}</span>'
        )        
    return docid_html



def process_results(results, highlight_terms=[]):
    if len(results) == 0:
        return """<br><p style='font-family: Arial; color:Silver; text-align: center;'>
                No results retrieved.</p><br><hr>"""

    results_html = ""
    for result in results:
        tokens = result["text"].split()
        tokens_html = []
        for token in tokens:
            if token in highlight_terms:
                tokens_html.append("<b>{}</b>".format(token))
            else:
                tokens_html.append(token)
        tokens_html = " ".join(tokens_html)
        tokens_html = process_pii(tokens_html)
        meta_html = (
            """
                <p class='underline-on-hover' style='font-size:12px; font-family: Arial; color:#585858; text-align: left;'>
                <a href='{}' target='_blank'>{}</a></p>""".format(
                result["meta"]["url"], result["meta"]["url"]
            )
            if "meta" in result and result["meta"] is not None and "url" in result["meta"]
            else ""
        )
        docid_html = get_docid_html(result["docid"])
        results_html += """{}
            <p style='font-size:14px; font-family: Arial; color:#7978FF; text-align: left;'>Document ID: {}</p>
            <p style='font-size:12px; font-family: Arial; color:MediumAquaMarine'>Language: {}</p>
            <p style='font-family: Arial;'>{}</p>
            <br>
        """.format(
            meta_html, docid_html, result["lang"], tokens_html
        )
    return results_html + "<hr>"

def search(query, language, num_results=10):
    searcher = _load_sparse_searcher(language=LANG_MAPPING[language])

    t_0 = time.time()
    search_results = searcher.search(query, k=num_results)
    search_time = time.time() - t_0

    results_dict ={"text": [], "docid": [], "score":[], "lang": language}
    for i, result in enumerate(search_results):
        result = json.loads(result.raw)
        results_dict["text"].append(result["contents"])
        results_dict["docid"].append(result["id"])
        results_dict["score"].append(search_results[i].score)

    return results_dict, search_time


description = """# <p style="text-align: center;"> "{{ cookiecutter.emoji }}" 🔎 {{ cookiecutter.space_title }} search tool 🔍 "{{ cookiecutter.emoji }}" </p>
{{ cookiecutter.space_description}}"""


if __name__ == "__main__":
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


        def submit(query, lang, k):
            query = query.strip()
            if query is None or query == "":
                return "", ""
            return {
                results: search(query, lang, k),
            }

        query.submit(fn=submit, inputs=[query, lang, k], outputs=[results])
        submit_btn.click(submit, inputs=[query, lang, k], outputs=[results])

    demo.launch(enable_queue=True, debug=True)