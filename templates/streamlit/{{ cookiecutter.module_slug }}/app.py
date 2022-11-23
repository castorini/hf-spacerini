# This currently contains Odunayo's template. We need to adapt this to cookiecutter.
import streamlit as st
from pyserini.search.lucene import LuceneSearcher
import json
import time

st.set_page_config(page_title="{{title}}", page_icon='', layout="centered")
searcher = LuceneSearcher('{{index_path}}')


col1, col2 = st.columns([9, 1])
with col1:
    search_query = st.text_input(label="", placeholder="Search")

with col2:
    st.write('#')
    button_clicked = st.button("🔎")


if search_query or button_clicked:
    num_results = None

    t_0 = time.time()
    search_results = searcher.search(search_query, k=100_000)
    search_time = time.time() - t_0

    st.write(f'<p align=\"right\" style=\"color:grey;\">Retrieved {len(search_results):,.0f} documents in {search_time*1000:.2f} ms</p>', unsafe_allow_html=True)
    for result in search_results[:10]:
        result = json.loads(result.raw)
        doc = result["contents"]
        result_id = result["id"]
        try:
            st.write(doc[:1000], unsafe_allow_html=True)
            st.write(f'<div align="right"><b>Document ID</b>: {result_id}</div>', unsafe_allow_html=True)

        except:
            pass

        st.write('---')