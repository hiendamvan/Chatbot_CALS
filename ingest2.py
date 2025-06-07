from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_cohere import CohereEmbeddings
from langchain_chroma import Chroma
from uuid import uuid4
import os
import json 
import pdfplumber 
from docx import Document 
import win32com.client as win32

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

def convert_doc_to_docx(doc_path):
    """
    Chuyển đổi một file .doc thành .docx bằng cách sử dụng Microsoft Word.
    Yêu cầu: Chạy trên Windows và có cài đặt MS Word.
    """
    # Tạo một đường dẫn tuyệt đối để Word có thể tìm thấy file
    doc_path_abs = os.path.abspath(doc_path)
    docx_path_abs = doc_path_abs + 'x'

    # Kiểm tra nếu file .docx đã tồn tại thì không cần convert nữa
    if os.path.exists(docx_path_abs):
        print(f"File .docx đã tồn tại: {docx_path_abs}")
        return docx_path_abs

    try:
        # Khởi tạo ứng dụng Word
        word = win32.gencache.EnsureDispatch('Word.Application')
        word.Visible = False # Chạy ẩn

        # Mở file .doc
        doc = word.Documents.Open(doc_path_abs)
        
        # Lưu file sang định dạng .docx (wdFormatXMLDocument = 12)
        doc.SaveAs(docx_path_abs, FileFormat=12)
        doc.Close()
        word.Quit()
        
        print(f"Đã chuyển đổi thành công: {docx_path_abs}")
        return docx_path_abs
    except Exception as e:
        print(f"Lỗi khi chuyển đổi file {doc_path}: {e}")
        # Đảm bảo Word được đóng lại nếu có lỗi
        if 'word' in locals() and word is not None:
            word.Quit()
        return None

def process_doc(file_path):
    """
    Hàm xử lý file .doc bằng cách chuyển nó sang .docx rồi xử lý.
    """
    print(f"Phát hiện file .doc, đang tiến hành chuyển đổi: {file_path}")
    docx_path = convert_doc_to_docx(file_path)
    
    if docx_path:
        # After converting, process the .docx file
        print("--- Bắt đầu xử lý file .docx vừa được chuyển đổi ---")
        process_docx(docx_path)
        

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
        if file_path.lower().endswith('.doc') == True: 
            process_doc(file_path)
            break
    break
