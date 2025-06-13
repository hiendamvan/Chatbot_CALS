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
            metadata = {
                "title": file_title,
                "source_file": file_path,
                "mediaTitle": doc.get("mediaTitle", ""),
            }
            text, tables = process_pdf(file_path)
            create_embedding(text, tables, metadata=metadata)
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

# text, tables = process_pdf("data/QLTT_1/2025/01/02/CD9DBAE7AA59551D3E8234C6696A56F5.pdf")
# print(len(text))
# # write to a file
# with open("data/processed_text.txt", "w", encoding="utf-8") as f:
#     f.write(text)