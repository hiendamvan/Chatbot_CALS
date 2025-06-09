from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_cohere import CohereEmbeddings
from langchain_chroma import Chroma
from uuid import uuid4
import os

from summary import summarize

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    is_separator_regex=False,
)

embedding = CohereEmbeddings(
    cohere_api_key=os.getenv('COHERE_API_KEY'), 
    model='embed-multilingual-v3.0'
)

vector_store = Chroma(
    collection_name='vcc_env',
    embedding_function=embedding,
    persist_directory='chroma_db'
)

def create_embedding(text, tables):
    ''''
    This function will: 
        1. Split the into chunks 
        2. Create unique IDs for each chunk
        3. Add the chunks to the vector store
    '''
    docs = text_splitter.split_text(text)

    # create the chunk 
    chunks = text_splitter.split_documents(docs)

    text_summaries = []
    for chunk in chunks:
        # summarize the chunk
        summary = summarize(chunk.page_content)
        text_summaries.append(summary)
    
    tables_summaries = []
    for table in tables:
        # summarize the table
        summary = summarize(table.to_string())
        tables_summaries.append(summary)
        
    # create unique ID's
    uuids = [str(uuid4()) for _ in range(len(chunks))]

    # add chunks to the vector store 
    vector_store.add_documents(documents=chunks, ids=uuids)