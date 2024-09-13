
from llama_index.core import SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline, IngestionCache
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.extractors import SummaryExtractor
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
import openai
from llama_index.core import VectorStoreIndex, load_index_from_storage
from llama_index.core import StorageContext
from cfg import INDEX_STORAGE
from cfg import STORAGE_PATH, CACHE_FILE
import requests
import re
import cfg
from db import id_exists, add_id

openai.api_key = cfg.api_key
Settings.llm = OpenAI(model=cfg.model, temperature=cfg.temperature)

def get_text(id, link):
    print(id)
    print(link)
    if id != "":
        getid = requests.get(f"https://api.tinthoisu.vn/articles/detail?id={id}")
    else:
        print("getlikkkk")
        getid = requests.get(f"https://api.tinthoisu.vn/articles/detail?link={link}")
    clus = getid.json()
    print(clus)
    try:
        cluster_id = clus['data']['item']['clusterId']
        a = requests.get(f'https://api.tinthoisu.vn/articles?clusterId={cluster_id}&size=100&offset=0')

        # Access the JSON content of the response using a.json()
        data = a.json()
        print(data)
        # Now you can access the data using indexing
        cnt = len(data['data']['items'])
        cnt1 = 6 if cnt > 6 else cnt
        text_content_list = [item['textContent'] for item in data['data']['items'][1:cnt1-1]]
        idd =cluster_id
        text_content = '\n'.join(text_content_list)
        print(text_content)
    except:
        print(clus)
        text_content = clus['data']['item']['textContent']
        idd = clus['data']['item']['id']
        print(idd)
        print(text_content)
    if id_exists(idd):
        return idd, "false"

    # Lưu vào file hung.txt
    with open(f"{cfg.STORE_TEXT}/{idd}.txt", 'w', encoding='utf-8') as text_file:
        text_file.write(text_content)
    return idd, "true"
def ingest_documents(idd):
    # Load documents, easy but we can't move data or share for another device.
    # Because document id is root file name when our input is a folder.
    # documents = SimpleDirectoryReader(
    #     STORAGE_PATH,
    #     filename_as_id = True
    # ).load_data()
    file_path = f"{cfg.STORE_TEXT}/{idd}.txt"
    documents = SimpleDirectoryReader(
        input_files=[file_path],
        filename_as_id = True
    ).load_data()
    for doc in documents:
        print(doc.id_)

    try:
        cached_hashes = IngestionCache.from_persist_path(
            CACHE_FILE
            )
        print("Cache file found. Running using cache...")
    except:
        cached_hashes = ""
        print("No cache file found. Running without cache...")
    pipeline = IngestionPipeline(
        transformations=[
            TokenTextSplitter(
                chunk_size=512,
                chunk_overlap=20
            ),
            #SummaryExtractor(summaries=['self'], prompt_template=CUSTORM_SUMMARY_EXTRACT_TEMPLATE),
            OpenAIEmbedding(
                model="text-embedding-3-small",
            )
        ],
        cache=cached_hashes
    )

    nodes = pipeline.run(documents=documents)
    pipeline.cache.persist(CACHE_FILE)

    return nodes
def build_indexes(nodes,idd):
    try:
        storage_context = StorageContext.from_defaults(
            persist_dir=INDEX_STORAGE
        )
        vector_index = load_index_from_storage(
            storage_context, index_id=str(idd)
        )
        print("All indices loaded from storage.")
    except Exception as e:
        print(f"Error occurred while loading indices: {e}")
        storage_context = StorageContext.from_defaults()
        vector_index = VectorStoreIndex(
            nodes, storage_context=storage_context
        )
        vector_index.set_index_id(str(idd))
        storage_context.persist(
            persist_dir=INDEX_STORAGE
        )
        print("New indexes created and persisted.")
    add_id(idd)
    return vector_index