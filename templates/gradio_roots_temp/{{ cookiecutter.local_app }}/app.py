import http.client as http_client
import json
import logging
import os
import re
import time
import string
import traceback

import gradio as gr
from typing import Callable, Optional, Tuple, Union, Dict, Any
from pyserini import util
from pyserini.search import LuceneSearcher, FaissSearcher, AutoQueryEncoder
from pyserini.index.lucene import IndexReader


Searcher = Union[FaissSearcher, LuceneSearcher]

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
    if "{{cookiecutter.private }}":
        docid_html = (
            f"<a "
            f'class="underline-on-hover"'
            f'style="color:#AA4A44;"'
            'href="https://huggingface.co/datasets/{{ cookiecutter.dataset_name }}"'
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

def fetch_index_stats(index_path: str) -> Dict[str, Any]:
    """
    Fetch index statistics
    index_path : str
        Path to index directory
    Returns
    -------
    Dictionary of index statistics
    Dictionary Keys ==> total_terms, documents, unique_terms
    """
    assert os.path.exists(index_path), f"Index path {index_path} does not exist"
    index_reader = IndexReader(index_path)
    return index_reader.stats()

def process_results(results, highlight_terms=[]):
    if len(results) == 0:
        return """<br><p style='font-family: Arial; color:Silver; text-align: center;'>
                No results retrieved.</p><br><hr>"""

    results_html = ""
    for i in range(len(results)):
        tokens = results["text"][i].split()
        tokens_html = []
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
        docid_html = get_docid_html(results["docid"][i])
        results_html += """{}
            <p style='font-size:20px; font-family: Arial; color:#7978FF; text-align: left;'>Document ID: {}</p>
            <p style='font-size:14px; font-family: Arial; color:#7978FF; text-align: left;'>Score: {}</p>
            <p style='font-size:12px; font-family: Arial; color:MediumAquaMarine'>Language: {}</p>
            <p style='font-family: Arial;font-size:15px;'>{}</p>
            <br>
        """.format(
            meta_html, docid_html, results["score"][i], results["lang"], tokens_html
        )
    return results_html + "<hr>"

def search(query, language, num_results=10):
    searcher = _load_sparse_searcher(language=language)

    t_0 = time.time()
    search_results = searcher.search(query, k=num_results)
    search_time = time.time() - t_0

    results_dict ={"text": [], "docid": [], "score":[], "lang": language}
    for i, result in enumerate(search_results):
        result = json.loads(result.raw)
        results_dict["text"].append(result["contents"])
        results_dict["docid"].append(result["id"])
        results_dict["score"].append(search_results[i].score)

    return process_results(results_dict)

stats = fetch_index_stats('index/')

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