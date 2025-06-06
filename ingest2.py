from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_cohere import CohereEmbeddings
from langchain_chroma import Chroma
from uuid import uuid4
import os
import json 

with open('data/document-list.json', 'r', encoding='utf-8') as f: 
    data = json.load(f)
    
documents = data["contents"]
print(len(documents))

for doc in documents:
    print(f"--- {doc['mediaTitle']} ---")
    for attach in doc.get("attachmentList", []):
        file_path = attach["url"]
        file_title = attach["title"]
        file_path = file_path.replace("/home/ctct_hdqt_owner/qltt_web_8882/Upload/QLTT", "data/QLTT_1")
        print(f"Tệp: {file_title} | Đường dẫn: {file_path}")
    break
