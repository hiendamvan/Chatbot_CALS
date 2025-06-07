from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_cohere import CohereEmbeddings
from langchain_chroma import Chroma
from uuid import uuid4
import os
import json 
import pdfplumber 
from docx import Document 

def process_docx(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return 
    
    doc = Document(file_path)
    for para in doc.paragraphs:
        # Extract text from paragraphs
        text = para.text.strip()
        if text:
            print(f'Paragraph: {text}')
        else:
            print("Empty paragraph found.")
        
    # Extract tables from the document 
    for table_idx, table in enumerate(doc.tables, start=1):
        print(f"\n🔹 Table {table_idx}:")
        for row in table.rows:
            row_data = [cell.text.strip() for cell in row.cells]
            print(row_data)
        
        if table_idx == 1:
            break
    
def process_pdf(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return 
    
    with pdfplumber.open(file_path) as pdf:
        for page_number, page in enumerate(pdf.pages):
            # Extract text from each page 
            text = page.extract_text()
            if text:
                print(f"Text length of page {page_number + 1}: {len(text)}.")
                #print(f"Page {page_number + 1} content:\n{text}\n")
            else:
                print(f"Page {page_number + 1} is empty or could not be read.")
            
            # Extract tables from each page
            tables = page.extract_tables()
            if tables:
                for table_idx, table in enumerate(tables, start=1):
                    print(f"\n🔹 Table {table_idx}:")
                    for row in table:
                        print(row)
            else:
                print("None of table.")
            
            if page_number == 1: 
                break


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
        if file_path.lower().endswith('.docx') == True: 
            process_docx(file_path)
            print("------------------------------------------")
    break
