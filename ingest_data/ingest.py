from uuid import uuid4
import json 
import win32com.client as win32
import pandas as pd

from create_embedding import create_embedding
from process_file import process_docx, process_pdf, process_doc

with open('data/document-list.json', 'r', encoding='utf-8') as f: 
    data = json.load(f)
    
documents = data["contents"]

for doc in documents:
    print(f"--- {doc['mediaTitle']} ---")
    for attach in doc.get("attachmentList", []):
        file_path = attach["url"]
        file_title = attach["title"]
        file_path = file_path.replace("/home/ctct_hdqt_owner/qltt_web_8882/Upload/QLTT", "data/QLTT_1")
        print(f"Tệp: {file_title} | Đường dẫn: {file_path}")
        if file_path.lower().endswith('.pdf') == True: 
            text, tables = process_pdf(file_path)
            create_embedding(text, tables)
            break
        # if file_path.lower().endswith('.docx') == True: 
        #     text, tables = process_docx(file_path)
        #     print(text)
        #     print(tables)
        #     create_embedding(text, tables)
        #     break
        # elif file_path.lower().endswith('.doc') == True:
        #     text, tables = process_doc(file_path)
        #     create_embedding(text, tables)
    break
