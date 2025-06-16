from uuid import uuid4
import json 
import win32com.client as win32
from create_embedding import create_embedding
from process_file import process_docx, process_pdf, process_doc

with open('data/document-list.json', 'r', encoding='utf-8') as f: 
    data = json.load(f)
    
documents = data["contents"]

# count number of documents 
cnt = 0
cnt_doc = 0
cnt_pdf = 0
cnt_docx = 0 
start_index = 790
current_index = 0

for doc in documents:
    print(f"--- {doc['mediaTitle']} ---")
    cnt += len(doc.get("attachmentList", []))
    print(cnt)
    for attach in doc.get("attachmentList", []):
        current_index += 1
        if current_index < start_index:
            continue
        file_path = attach["url"]
        file_title = attach["title"]
        file_path = file_path.replace("/home/ctct_hdqt_owner/qltt_web_8882/Upload/QLTT", "data/QLTT_1")
        print(f"Tệp: {file_title} | Đường dẫn: {file_path}")
        metadata = {
            "title": file_title,
            "source_file": file_path,
            "mediaTitle": doc.get("mediaTitle", ""),
        }
        
        if file_path.lower().endswith('.pdf') == True:
            cnt_pdf += 1
            text= process_pdf(file_path)
            try:
                create_embedding(text, metadata=metadata)
            except Exception as e:
                print(f"Error processing PDF {file_path}: {e}")
                continue
            
        if file_path.lower().endswith('.docx') == True: 
            cnt_docx+=1
            text = process_docx(file_path)
            try:
                create_embedding(text, metadata=metadata)
            except Exception as e:
                print(f"Error processing PDF {file_path}: {e}")
                continue
            
        elif file_path.lower().endswith('.doc') == True:
            cnt_doc += 1
            # text, tables = process_doc(file_path)
            # create_embedding(text, tables, metadata=metadata)

# text, tables = process_pdf("data/QLTT_1/2025/01/02/CD9DBAE7AA59551D3E8234C6696A56F5.pdf")
# print(len(text))
# # write to a file
# with open("data/processed_text.txt", "w", encoding="utf-8") as f:
#     f.write(text)

# Total documents: 876
# Total PDF files: 665
# Total DOCX files: 113
# Total DOC files: 33