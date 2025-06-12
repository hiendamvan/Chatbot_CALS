from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_core.documents import Document
from langchain_chroma import Chroma
from uuid import uuid4
import os


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    is_separator_regex=False,
)

embedding = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-small"
)

vector_store = Chroma(
    collection_name='vcc_env',
    embedding_function=embedding,
    persist_directory='chroma_db'
)

def create_embedding(text, tables):
    ''''
    This function will: 
        1. Split the text into chunks 
        2. Summarize chunks and tables
        3. Create unique IDs for each chunk
        4. Add the chunks to the vector store
    '''
    # Step 1: Split the text into chunks
    docs = [Document(page_content=text)]
    # create the chunk 
    print("Splitting text into chunks...")
    chunks = text_splitter.split_documents(docs)

    # # Step 2: Summarize the text and tables 
    # print("Summarizing chunks and tables...")
    # summary_chunks = []
    # for chunk in chunks:
    #     summary_text = summarize(chunk.page_content)
    #     summary_doc = Document(
    #         page_content=summary_text,
    #         metadata={"source":"text_summary"}
    #     )
    #     summary_chunks.append(summary_doc)
    
    # for table in tables:
    #     summary_text = summarize(table.to_string())
    #     summary_doc = Document(
    #         page_content=summary_text,
    #         metadata={"source":"text_summary"}
    #     )
    #     summary_chunks.append(summary_doc)
    
    # create unique ID's
    uuids = [str(uuid4()) for _ in range(len(chunks))]

    # add chunks to the vector store 
    print("Adding documents to the vector store...")
    vector_store.add_documents(documents=chunks, ids=uuids)