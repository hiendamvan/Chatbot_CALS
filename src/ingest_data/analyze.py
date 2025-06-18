import json 

with open('data/document-list.json', 'r', encoding='utf-8') as f: 
    data = json.load(f)
    
documents = data["contents"]

# count number of documents 
cnt = 0
cnt_doc = 0
cnt_pdf = 0
cnt_docx = 0 

for doc in documents:
    print(f"--- {doc['mediaTitle']} ---")
    cnt += len(doc.get("attachmentList", []))
    print(cnt)
    if cnt > 100: 
        break
    for attach in doc.get("attachmentList", []):
        file_path = attach["url"]
        file_title = attach["title"]
        file_path = file_path.replace("/home/ctct_hdqt_owner/qltt_web_8882/Upload/QLTT", "data/QLTT_1")
        metadata = {
            "title": file_title,
            "source_file": file_path,
            "mediaTitle": doc.get("mediaTitle", ""),
        }
        
        if file_path.lower().endswith('.pdf') == True:
            cnt_pdf += 1
            
        if file_path.lower().endswith('.docx') == True: 
            cnt_docx+=1
            
        elif file_path.lower().endswith('.doc') == True:
            cnt_doc += 1
            

print(len(documents))
print(f"Total documents: {cnt}")
print(f"Total PDF files: {cnt_pdf}")
print(f"Total docx files: {cnt_docx}")
print(f"Total doc files: {cnt_doc}")
# Total documents: 876
# Total PDF files: 665
# Total DOCX files: 113
# Total DOC files: 33