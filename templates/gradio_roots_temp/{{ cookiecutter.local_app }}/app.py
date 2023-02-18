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
    data_org, dataset, docid = docid.split("/")
    metadata = roots_datasets[dataset]
    if metadata.private:
        docid_html = (
            f"<a "
            f'class="underline-on-hover"'
            f'title="This dataset is private. See the introductory text for more information"'
            f'style="color:#AA4A44;"'
            f'href="https://huggingface.co/datasets/bigscience-data/{dataset}"'
            f'target="_blank"><b>🔒{dataset}</b></a><span style="color: #7978FF;">/{docid}</span>'
        )
    else:
        docid_html = (
            f"<a "
            f'class="underline-on-hover"'
            f'title="This dataset is licensed {metadata.tags[0].split(":")[-1]}"'
            f'style="color:#2D31FA;"'
            f'href="https://huggingface.co/datasets/bigscience-data/{dataset}"'
            f'target="_blank"><b>{dataset}</b></a><span style="color: #7978FF;">/{docid}</span>'
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


def scisearch(query, language, num_results=10):
    try:
        query = " ".join(query.split())
        if query == "" or query is None:
            return ""

        post_data = {"query": query, "k": num_results}
        if language != "detect_language":
            post_data["lang"] = language

        output = requests.post(
            os.environ.get("address"),
            headers={"Content-type": "application/json"},
            data=json.dumps(post_data),
            timeout=60,
        )

        payload = json.loads(output.text)

        if "err" in payload:
            if payload["err"]["type"] == "unsupported_lang":
                detected_lang = payload["err"]["meta"]["detected_lang"]
                return f"""
                    <p style='font-size:18px; font-family: Arial; color:MediumVioletRed; text-align: center;'>
                    Detected language <b>{detected_lang}</b> is not supported.<br>
                    Please choose a language from the dropdown or type another query.
                    </p><br><hr><br>"""

        results = payload["results"]
        highlight_terms = payload["highlight_terms"]

        if language == "detect_language":
            results = list(results.values())[0]
            return (
                (
                    f"""<p style='font-family: Arial; color:MediumAquaMarine; text-align: center; line-height: 3em'>
                Detected language: <b>{results[0]["lang"]}</b></p><br><hr><br>"""
                    if len(results) > 0 and language == "detect_language"
                    else ""
                )
                + process_results(results, highlight_terms)
            )

        if language == "all":
            results_html = ""
            for lang, results_for_lang in results.items():
                if len(results_for_lang) == 0:
                    results_html += f"""<p style='font-family: Arial; color:Silver; text-align: left; line-height: 3em'>
                            No results for language: <b>{lang}</b><hr></p>"""
                    continue

                collapsible_results = f"""
                    <details>
                        <summary style='font-family: Arial; color:MediumAquaMarine; text-align: left; line-height: 3em'>
                            Results for language: <b>{lang}</b><hr>
                        </summary>
                        {process_results(results_for_lang, highlight_terms)}
                    </details>"""
                results_html += collapsible_results
            return results_html

        results = list(results.values())[0]
        return process_results(results, highlight_terms)

    except Exception as e:
        results_html = f"""
                <p style='font-size:18px; font-family: Arial; color:MediumVioletRed; text-align: center;'>
                Raised {type(e).__name__}</p>
                <p style='font-size:14px; font-family: Arial; '>
                Check if a relevant discussion already exists in the Community tab. If not, please open a discussion.
                </p>
            """
        print(e)
        print(traceback.format_exc())

    return results_html


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
                results: scisearch(query, lang, k),
            }

        query.submit(fn=submit, inputs=[query, lang, k], outputs=[results])
        submit_btn.click(submit, inputs=[query, lang, k], outputs=[results])

    demo.launch(enable_queue=True, debug=True)