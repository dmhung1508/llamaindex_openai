from create_node import get_text, ingest_documents, build_indexes
from cfg import *
from load_chat import load_chat_store, initialize_chatbot, chat_interface
from fastapi import FastAPI
from pydantic import BaseModel,validator
import uvicorn
from openai import OpenAI
from typing import Optional
from db import add_comment_if_not_exists
from typing import List
# idd = get_text("66e31f096adc81284f118a4f")
# if idd != "none":
#     nodes = ingest_documents(idd)
#     vector_index = build_indexes(nodes,idd)
# chat_store = load_chat_store()
# agent = initialize_chatbot(chat_store, "dmhung", "66e31f096adc81284f118a4f")
# tex = input("Text: ")
# text = chat_interface(agent, chat_store, tex)
# print(text)
app = FastAPI()
class text_sample(BaseModel):
    userId: str
    articleId: Optional[str] = None
    articleLink: Optional[str] = None
    text: str
class binhluan(BaseModel):
    articleId: Optional[str] = None
    articleLink: Optional[str] = None
    text: str
@app.get("/")
def read_root():
    return "USE POST"

@app.post("/chat")
async def chat(item: text_sample):
    idd,check = get_text(item.articleId, item.articleLink)
    if check == "true":
        nodes = ingest_documents(idd)
        vector_index = build_indexes(nodes,idd)
    chat_store = load_chat_store()
    user_id = item.userId+"_"+ str(idd)

    agent = initialize_chatbot(chat_store, str(user_id), str(idd))
    try:
        text = chat_interface(agent, chat_store, item.text)
        return {"status": "ok", "text": text}
    except:
        return {"status": "false"}
@app.post("/binhluan")
async def chat(item: binhluan):

    response = add_comment_if_not_exists(item.articleId, item.articleLink, item.text)
    return {"status": "ok", "text": response}

if __name__ == "__main__":
    uvicorn.run(app, port=4555)