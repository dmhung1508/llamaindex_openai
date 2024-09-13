import nest_asyncio
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    load_index_from_storage,
    StorageContext,
    Settings
)
from llama_index.core.ingestion import IngestionPipeline, IngestionCache
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.extractors import SummaryExtractor
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
import openai

import streamlit as st
from cfg import (

    STORAGE_PATH,
    CACHE_FILE,
    INDEX_STORAGE,
    CONVERSATION_FILE,
    SCORES_FILE,
    CUSTORM_SUMMARY_EXTRACT_TEMPLATE,
    SYSTEM_PROMPT,
    api_key,
    model,
    temperature
)
import cfg
print(model)
openai.api_key = api_key
Settings.llm = OpenAI(model=cfg.model, temperature=temperature)
import os
import json
from datetime import datetime
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import QueryEngineTool, ToolMetadata, FunctionTool
from llama_index.agent.openai import OpenAIAgent
from llama_index.core.storage.chat_store import SimpleChatStore
from create_node import get_text, ingest_documents, build_indexes

def load_chat_store():
    if os.path.exists(CONVERSATION_FILE) and os.path.getsize(CONVERSATION_FILE) > 0:
        try:
            chat_store = SimpleChatStore.from_persist_path(CONVERSATION_FILE)
        except json.JSONDecodeError:
            chat_store = SimpleChatStore()
    else:
        chat_store = SimpleChatStore()
    return chat_store
def initialize_chatbot(chat_store, username, idd):
    memory = ChatMemoryBuffer.from_defaults(
        token_limit=3000,
        chat_store=chat_store,
        chat_store_key= username
    )
    storage_context = StorageContext.from_defaults(
        persist_dir=INDEX_STORAGE
    )
    index = load_index_from_storage(
        storage_context, index_id=idd
    )
    dsm5_engine = index.as_query_engine(
        similarity_top_k=3,
    )
    dsm5_tool= QueryEngineTool.from_defaults(query_engine=dsm5_engine,
                                           description="Công cụ tìm kiếm thông tin về câu hỏi của người dùng liên quan đến bài báo, đó có thể là một câu tranh luận, một câu hỏi tìm kiếm thông tin hay là lời phê bình bài báo")

    agent = OpenAIAgent.from_tools(
        tools=[dsm5_tool],
        memory=memory,
        system_prompt=SYSTEM_PROMPT,
        verbose=True
    )
    return agent
def chat_interface(agent, chat_store,prompt):
    response = str(agent.chat(prompt))
    chat_store.persist(CONVERSATION_FILE)
    return response

