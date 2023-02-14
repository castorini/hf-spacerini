import gradio as gr
from datasets import load_from_disk
from pyserini.search.lucene import LuceneSearcher

searcher = LuceneSearcher("index")
ds = load_from_disk("data")
PAGINATION_VISIBLE = True
NUM_PAGES = 10 # STATIC. THIS CAN'T CHANGE BECAUSE GRADIO CAN'T DYNAMICALLY CREATE COMPONENTS. 
RESULTS_PER_PAGE = 5 

TEXT_FIELD = "{{ cookiecutter.dset_text_field }}"
METADATA_FIELD = "{{ cookiecutter.metadata_field }}"

def result_html(result, meta):
    return (
    f"<div style=\"color:#2a5cb3;font-weight: 500\"><u>{meta}</u></div><br>"
    f"<div><details><summary>{result[:250]}...</summary><p>{result[250:]}</p></details></div><br><hr><br>"
    )

def format_results(results):
    return "\n".join([result_html(result, meta) for result,meta in zip(results[TEXT_FIELD], results[METADATA_FIELD])])
    
def page_0(query):
    hits = searcher.search(query, k=NUM_PAGES*RESULTS_PER_PAGE)
    ix = [int(hit.docid) for hit in hits]
    results = ds.select(ix).shard(num_shards=NUM_PAGES, index=0, contiguous=True) # no need to shard. split ix in batches instead. (would make sense if results was cacheable)
    results = format_results(results)
    return results, [ix]

def page_i(i, ix):
    ix = ix[0]
    results = ds.select(ix).shard(num_shards=NUM_PAGES, index=i, contiguous=True)
    results = format_results(results)
    return results, [ix]
    
with gr.Blocks(css="#b {min-width:15px;background:transparent;border:white;box-shadow:none;}") as demo: #
    with gr.Row():
        gr.Markdown(value="""## <p style="text-align: center;"> {{ cookiecutter.space_title }} </p>""")  
    with gr.Row():
        with gr.Column(scale=1):
            result_list = gr.Dataframe(type="array", visible=False, col_count=1)      
        with gr.Column(scale=13):
            query = gr.Textbox(lines=1, max_lines=1, placeholder="Search…", label="")
        with gr.Column(scale=1):
            with gr.Row(scale=1):
                pass
            with gr.Row(scale=1):    
                submit_btn = gr.Button("🔍", elem_id="b").style(full_width=False)
            with gr.Row(scale=1):
                pass
                
    with gr.Row():
        with gr.Column(scale=1):
            pass
        with gr.Column(scale=13):
            c = gr.HTML(label="Results")
            with gr.Row():
                # left = gr.Button(value="◀", elem_id="b", visible=False).style(full_width=True)
                page_1 = gr.Button(value="1", elem_id="b", visible=PAGINATION_VISIBLE).style(full_width=True)
                page_2 = gr.Button(value="2", elem_id="b", visible=PAGINATION_VISIBLE).style(full_width=True)
                page_3 = gr.Button(value="3", elem_id="b", visible=PAGINATION_VISIBLE).style(full_width=True)
                page_4 = gr.Button(value="4", elem_id="b", visible=PAGINATION_VISIBLE).style(full_width=True)
                page_5 = gr.Button(value="5", elem_id="b", visible=PAGINATION_VISIBLE).style(full_width=True)
                page_6 = gr.Button(value="6", elem_id="b", visible=PAGINATION_VISIBLE).style(full_width=True)
                page_7 = gr.Button(value="7", elem_id="b", visible=PAGINATION_VISIBLE).style(full_width=True)
                page_8 = gr.Button(value="8", elem_id="b", visible=PAGINATION_VISIBLE).style(full_width=True)
                page_9 = gr.Button(value="9", elem_id="b", visible=PAGINATION_VISIBLE).style(full_width=True)
                page_10 = gr.Button(value="10", elem_id="b", visible=PAGINATION_VISIBLE).style(full_width=True)
                # right = gr.Button(value="▶", elem_id="b", visible=False).style(full_width=True)
        with gr.Column(scale=1):
            pass
    query.submit(fn=page_0, inputs=[query], outputs=[c, result_list])
    submit_btn.click(page_0, inputs=[query], outputs=[c, result_list])
    with gr.Box(visible=False):
        nums = [gr.Number(i, visible=False, precision=0) for i in range(NUM_PAGES)]
    page_1.click(fn=page_i, inputs=[nums[0], result_list], outputs=[c, result_list])
    page_2.click(fn=page_i, inputs=[nums[1], result_list], outputs=[c, result_list])
    page_3.click(fn=page_i, inputs=[nums[2], result_list], outputs=[c, result_list])
    page_4.click(fn=page_i, inputs=[nums[3], result_list], outputs=[c, result_list])
    page_5.click(fn=page_i, inputs=[nums[4], result_list], outputs=[c, result_list])
    page_6.click(fn=page_i, inputs=[nums[5], result_list], outputs=[c, result_list])
    page_7.click(fn=page_i, inputs=[nums[6], result_list], outputs=[c, result_list])
    page_8.click(fn=page_i, inputs=[nums[7], result_list], outputs=[c, result_list])
    page_9.click(fn=page_i, inputs=[nums[8], result_list], outputs=[c, result_list])
    page_10.click(fn=page_i, inputs=[nums[9], result_list], outputs=[c, result_list])
demo.launch(enable_queue=True, debug=True)