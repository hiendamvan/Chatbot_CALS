from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_cohere import CohereEmbeddings
from langchain_chroma import Chroma
from uuid import uuid4
import os

# import env file
from dotenv import load_dotenv
load_dotenv()

# configuration 
DATA_PATH = r'data'
CHROMA_PATH = r'chroma_db'

# initialize the embedding model 
embedding = CohereEmbeddings(
    cohere_api_key=os.getenv('COHERE_API_KEY'), 
    model='embed-multilingual-v3.0'
)

# initialize the vector store
vector_store = Chroma(
    collection_name='vcc_env',
    embedding_function=embedding,
    persist_directory=CHROMA_PATH
)

# load pdf documents 
pdf_loader = PyPDFDirectoryLoader(DATA_PATH)
raw_doc = pdf_loader.load()

# create splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 300, 
    chunk_overlap = 100,
    length_function = len, 
    is_separator_regex=False,
)

# create the chunk 
chunks = text_splitter.split_documents(raw_doc)

# create unique ID's
uuids = [str(uuid4()) for _ in range(len(chunks))]

# add chunks to the vector store 
vector_store.add_documents(documents=chunks, ids=uuids)