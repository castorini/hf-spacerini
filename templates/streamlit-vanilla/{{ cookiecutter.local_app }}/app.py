import streamlit as st
from chatnoir_api.v1 import search

st.set_page_config(
    page_title="ChatNoir",
    page_icon="🐈",
    layout="centered"
)

@st.cache(suppress_st_warning=True, allow_output_mutation=True, show_spinner=False)
def search_chat_noir(key, search_query):
    return search(api_key=key, query=search_query)

def result_html(result):
    return (
    f"<div style=\"color:#2a5cb3;font-weight: 500\">{(result.title.html).replace('<em>', '<b>').replace('</em>','</b>')}</div>"
    f"<a href=\"{result.target_uri}\" style=\"color:Green;\">{result.target_uri}</a>:<br>"
    f"<div>{(result.snippet.html).replace('<em>', '<b>').replace('</em>','</b>')}</div><br>"
    )

cola, colb, colc = st.columns([5,4,5])
with colb:
    st.image("https://www.chatnoir.eu/static/img/chatnoir.svg")

col1, col2 = st.columns([9, 1])
with col1:
    search_query = st.text_input(label="",
                placeholder="Search"
            )

with col2:
    st.write('#')
    button_clicked = st.button("🔎")


if search_query or button_clicked:
    search_results = search_chat_noir(st.secrets["key"], search_query)
    for result in search_results[:10]:
        st.write(result_html(result), unsafe_allow_html=True)
    
with st.expander("🐈 About", expanded=False):
    st.markdown(
        """
        This is a **work in progress** streamlit version of our [ChatNoir](https://www.chatnoir.eu/) search engine. ChatNoir is an Elasticsearch-based search engine offering a freely accessible search interface for the two ClueWeb corpora and the Common Crawl, together about 3 billion web pages. This version of the search engine uses the [Search API](https://www.chatnoir.eu/doc/api/) by way of the Python [chatnoir-api] Package and is therefore not as fast as the main site.

If you find this project useful in your research, please consider citing:
 
```
@InProceedings{bevendorff:2018,
  address =               {Berlin Heidelberg New York},
  author =                {Janek Bevendorff and Benno Stein and Matthias Hagen and Martin Potthast},
  booktitle =             {Advances in Information Retrieval. 40th European Conference on IR Research (ECIR 2018)},
  editor =                {Leif Azzopardi and Allan Hanbury and Gabriella Pasi and Benjamin Piwowarski},
  ids =                   {potthast:2018c,stein:2018c},
  month =                 mar,
  publisher =             {Springer},
  series =                {Lecture Notes in Computer Science},
  site =                  {Grenoble, France},
  title =                 {{Elastic ChatNoir: Search Engine for the ClueWeb and the Common Crawl}},
  year =                  2018
}
```
	    """
    )